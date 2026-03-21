import pickle
import time
from unittest.mock import MagicMock, patch

import pytest
from src.infrastructure.services.redis_task_queue_service import RedisTaskQueueService

# Dummy functions for pickling tests (must be module-level)
def dummy_func(a, b):
    return a + b

def task_func(val):
    # This is a bit tricky since we can't easily capture results in a global
    # without a global list or similar.
    global _test_results
    _test_results.append(val)

def failing_func():
    raise ValueError("Expected error")

def success_func():
    global _test_results
    _test_results.append("ok")

_test_results = []

@pytest.mark.Dependencies
class TestRedisTaskQueueService:
    @pytest.fixture(autouse=True)
    def clear_results(self):
        global _test_results
        _test_results = []
        yield
        _test_results = []

    @patch("redis.Redis")
    def test_enqueue_pushes_to_redis(self, mock_redis_cls):
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis

        svc = RedisTaskQueueService(queue_name="test_queue")

        svc.enqueue(dummy_func, 1, 2, task_title="Test Task", metadata={"key": "val"})

        # Verify lpush was called
        assert mock_redis.lpush.called
        args, _ = mock_redis.lpush.call_args
        assert args[0] == "test_queue"
        
        # Verify pickled data
        pushed_data = pickle.loads(args[1])
        assert pushed_data["task_title"] == "Test Task"
        assert pushed_data["metadata"] == {"key": "val"}
        assert pickle.loads(pushed_data["func"]) == dummy_func
        assert pickle.loads(pushed_data["args"]) == (1, 2)

    @patch("redis.Redis")
    def test_worker_processes_task(self, mock_redis_cls):
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis

        svc = RedisTaskQueueService(queue_name="test_queue", num_workers=1)

        # Prepare task data for brpop
        task_data = {
            "func": pickle.dumps(task_func),
            "args": pickle.dumps(("success",)),
            "kwargs": pickle.dumps({}),
            "task_title": "Worker Task",
        }
        data_blob = pickle.dumps(task_data)

        # Mock brpop to return the task once, then None (timeout)
        mock_redis.brpop.side_effect = [("test_queue", data_blob), None]

        svc.start()

        # Wait a bit for worker to process
        timeout = 2.0
        start = time.time()
        while not _test_results and (time.time() - start < timeout):
            time.sleep(0.1)

        svc.stop()

        assert "success" in _test_results
        assert mock_redis.brpop.called

    @patch("redis.Redis")
    def test_worker_handles_exception(self, mock_redis_cls):
        mock_redis = MagicMock()
        mock_redis_cls.return_value = mock_redis

        svc = RedisTaskQueueService(queue_name="test_queue", num_workers=1)

        task_data = {
            "func": pickle.dumps(failing_func),
            "args": pickle.dumps(()),
            "kwargs": pickle.dumps({}),
        }
        data_blob = pickle.dumps(task_data)

        success_blob = pickle.dumps({
            "func": pickle.dumps(success_func),
            "args": pickle.dumps(()),
            "kwargs": pickle.dumps({}),
        })

        mock_redis.brpop.side_effect = [("test_queue", data_blob), ("test_queue", success_blob), None]

        svc.start()
        
        timeout = 2.0
        start = time.time()
        while not _test_results and (time.time() - start < timeout):
            time.sleep(0.1)

        svc.stop()

        assert "ok" in _test_results
