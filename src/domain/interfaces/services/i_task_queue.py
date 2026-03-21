from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional


class ITaskQueue(ABC):
    """Interface for a task queue that can execute functions in the background."""

    @abstractmethod
    def start(self):
        """Starts the worker(s)."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the worker(s)."""
        pass

    @abstractmethod
    def enqueue(
        self,
        func: Callable,
        *args,
        task_title: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs,
    ):
        """Adds a task to the queue."""
        pass
