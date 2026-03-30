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
        """Publishes a JSON message to a Redis channel with UUID support."""
        import uuid

        def _json_serial(obj):
            if isinstance(obj, (uuid.UUID,)):
                return str(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        try:
            payload = json.dumps(message, default=_json_serial, ensure_ascii=False)
            self._redis.publish(channel, payload)
        except Exception:
            # Fallback to string representation if even custom serial fails
            try:
                self._redis.publish(channel, str(message))
            except Exception:
                pass

    def subscribe(self, channel: str):
        """Subscribes to a Redis channel and yields messages as they arrive."""
        pubsub = self._redis.pubsub()
        pubsub.subscribe(channel)

        for message in pubsub.listen():
            if message["type"] == "message":
                yield json.loads(message["data"])
