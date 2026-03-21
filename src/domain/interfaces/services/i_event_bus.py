from abc import ABC, abstractmethod
from typing import Any, Dict


class IEventBus(ABC):
    """Interface for an event bus that allows publishing and subscribing to events."""

    @abstractmethod
    def publish(self, channel: str, message: Dict[str, Any]):
        """Publishes a message to a channel."""
        pass

    @abstractmethod
    def subscribe(self, channel: str):
        """Returns a generator that yields messages from a channel."""
        pass
