"""Background job manager for running functions in a threadpool and tracking status.

Simple API:
- submit_job(fn, *args, **kwargs) -> job_id
- list_jobs() -> dict of job metadata (does not include Future)
- get_job(job_id) -> metadata or None
- mark_notified(job_id) -> mark job as already notified (used by UI)

Additionally provides a tiny HTTP status server (localhost) so the browser can poll
job statuses without requiring a full Streamlit reload. This server is only used in
development / local environments and is intentionally lightweight.

This module uses a ThreadPoolExecutor and keeps an in-memory registry. It is intentionally
lightweight and has no Streamlit dependencies so it is safe to import from UI modules.
"""
from __future__ import annotations

import http.server
import json
import socketserver
import threading
import urllib.parse
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict

_LOCK = threading.Lock()
_EXECUTOR = ThreadPoolExecutor(max_workers=3)
_JOBS: Dict[str, Dict[str, Any]] = {}

# Status server globals
_STATUS_SERVER = None
_STATUS_THREAD = None
_STATUS_PORT: int | None = None


def submit_job(fn: Callable, *args, **kwargs) -> str:
    """Submit a callable to run in background. Returns a job_id string.

    The callable will be executed in a worker thread. The job registry keeps simple
    metadata (status/result/exception/notified). The 'future' object is stored
    internally but not returned by list_jobs()/get_job to avoid leaking non-serializable
    objects to callers.
    """
    job_id = str(uuid.uuid4())
    with _LOCK:
        _JOBS[job_id] = {
            "id": job_id,
            "status": "running",
            "result": None,
            "exception": None,
            "notified": False,
            "future": None,
        }

    def _wrapper():
        try:
            res = fn(*args, **kwargs)
            with _LOCK:
                _JOBS[job_id]["status"] = "done"
                # store a short string representation of the result
                try:
                    _JOBS[job_id]["result"] = str(res)
                except Exception:
                    _JOBS[job_id]["result"] = "<unrepresentable result>"
        except Exception as e:
            with _LOCK:
                _JOBS[job_id]["status"] = "error"
                _JOBS[job_id]["exception"] = str(e)

    future = _EXECUTOR.submit(_wrapper)
    with _LOCK:
        _JOBS[job_id]["future"] = future
    return job_id


def list_jobs() -> Dict[str, Dict[str, Any]]:
    """Return a shallow copy of job metadata for all jobs (excluding Future objects)."""
    with _LOCK:
        out = {}
        for jid, j in _JOBS.items():
            out[jid] = {k: v for k, v in j.items() if k != "future"}
        return out


def get_job(job_id: str) -> Dict[str, Any] | None:
    """Return metadata for a single job or None if not found."""
    with _LOCK:
        j = _JOBS.get(job_id)
        if not j:
            return None
        return {k: v for k, v in j.items() if k != "future"}


def mark_notified(job_id: str) -> None:
    """Mark a job as notified so UI won't show duplicate notifications."""
    with _LOCK:
        if job_id in _JOBS:
            _JOBS[job_id]["notified"] = True


# Tiny HTTP status server so client-side JS can poll job statuses.
class _StatusHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # suppress default logging
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != '/jobs':
            self.send_response(404)
            self.end_headers()
            return
        qs = urllib.parse.parse_qs(parsed.query)
        ids = []
        if 'ids' in qs and qs['ids']:
            ids = qs['ids'][0].split(',')

        with _LOCK:
            if ids:
                resp = {jid: {k: v for k, v in _JOBS[jid].items() if k != 'future'} for jid in ids if jid in _JOBS}
            else:
                resp = {jid: {k: v for k, v in j.items() if k != 'future'} for jid, j in _JOBS.items()}

        body = json.dumps(resp)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        try:
            self.wfile.write(body.encode('utf-8'))
        except BrokenPipeError:
            pass


def ensure_status_server_running(port: int = 0) -> int:
    """Ensure the HTTP status server is running. Returns the bound port.

    The server binds to localhost only. Pass port=0 to get an ephemeral port.
    """
    global _STATUS_SERVER, _STATUS_THREAD, _STATUS_PORT
    if _STATUS_SERVER is not None:
        return _STATUS_PORT

    server = socketserver.ThreadingTCPServer(('127.0.0.1', port), _StatusHandler)
    server.allow_reuse_address = True
    _STATUS_PORT = server.server_address[1]

    def _serve():
        try:
            server.serve_forever()
        except Exception:
            pass

    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    _STATUS_SERVER = server
    _STATUS_THREAD = t
    return _STATUS_PORT


def stop_status_server() -> None:
    """Stop the status HTTP server if running."""
    global _STATUS_SERVER, _STATUS_THREAD, _STATUS_PORT
    if _STATUS_SERVER is None:
        return
    try:
        _STATUS_SERVER.shutdown()
        _STATUS_SERVER.server_close()
    except Exception:
        pass
    _STATUS_SERVER = None
    _STATUS_THREAD = None
    _STATUS_PORT = None


# Optional helper for tests/cleanup
def _clear_all_for_tests() -> None:
    with _LOCK:
        _JOBS.clear()
