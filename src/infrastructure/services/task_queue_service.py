import queue
import threading
import time
from typing import Callable

from src.config.logger import Logger

logger = Logger()


class TaskQueueService:
    """In-memory task queue with a background worker thread.

    This helps serialize heavy ingestion tasks to avoid concurrency issues
    and model/tokenizer borrow conflicts.
    """

    def __init__(self, num_workers: int = 1):
        self._queue: queue.Queue = queue.Queue()
        self._workers: list[threading.Thread] = []
        self._num_workers = num_workers
        self._should_stop = False

    def start(self):
        """Starts the background worker threads."""
        if self._workers:
            logger.warning("TaskQueueService already started.")
            return

        self._should_stop = False
        for i in range(self._num_workers):
            t = threading.Thread(
                target=self._worker_loop, name=f"TaskQueueWorker-{i}", daemon=True
            )
            t.start()
            self._workers.append(t)
        logger.info(f"TaskQueueService started with {self._num_workers} workers.")

    def stop(self):
        """Signals workers to stop and waits for them to finish."""
        logger.info("Stopping TaskQueueService...")
        self._should_stop = True

        # Add 'None' poison pills to wake up workers from block
        for _ in range(self._num_workers):
            self._queue.put(None)

        for t in self._workers:
            t.join(timeout=5.0)

        self._workers = []
        logger.info("TaskQueueService stopped.")

    def enqueue(self, func: Callable, *args, **kwargs):
        """Adds a task to the queue."""
        self._queue.put((func, args, kwargs))
        logger.debug(
            f"Task enqueued: {func.__name__}. Queue size: {self._queue.qsize()}"
        )

    def _worker_loop(self):
        """Infinite loop for the worker thread."""
        while not self._should_stop:
            try:
                item = self._queue.get(block=True, timeout=1.0)
                if item is None:
                    self._queue.task_done()
                    break

                func, args, kwargs = item

                logger.info(f"Worker processing task: {func.__name__}")
                start_time = time.time()

                try:
                    func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.info(f"Task {func.__name__} completed in {duration:.2f}s")
                except Exception as e:
                    logger.error(
                        f"Error executing task {func.__name__}: {e}",
                        context={"error": str(e)},
                    )
                finally:
                    self._queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Unexpected error in TaskQueue worker loop: {e}")
                time.sleep(1.0)  # Avoid tight loop on repeated errors
