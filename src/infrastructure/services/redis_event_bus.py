import json
from typing import Any, Dict

import redis
from src.config.settings import settings
from src.domain.interfaces.services.i_event_bus import IEventBus


class RedisEventBus(IEventBus):
    """Redis-backed event bus using Pub/Sub."""

    def __init__(self):
        self._redis = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            password=settings.redis.password,
            decode_responses=True,
        )

    def publish(self, channel: str, message: Dict[str, Any]):
        """Publishes a JSON message to a Redis channel."""
        self._redis.publish(channel, json.dumps(message))

    def subscribe(self, channel: str):
        """Subscribes to a Redis channel and yields messages as they arrive."""
        pubsub = self._redis.pubsub()
        pubsub.subscribe(channel)

        for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])
