from typing import Any, Optional


class ServiceRegistry:
    _instance = None
    _services: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
        return cls._instance

    def register(self, name: str, service: Any):
        self._services[name] = service

    def get(self, name: str) -> Optional[Any]:
        return self._services.get(name)


registry = ServiceRegistry()
