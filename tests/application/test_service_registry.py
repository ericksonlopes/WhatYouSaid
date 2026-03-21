import pytest
from src.application.service_registry import ServiceRegistry, registry

class TestServiceRegistry:
    def test_singleton(self):
        r1 = ServiceRegistry()
        r2 = ServiceRegistry()
        assert r1 is r2
        assert r1 is registry

    def test_register_and_get(self):
        dummy_service = {"key": "value"}
        registry.register("dummy", dummy_service)
        assert registry.get("dummy") == dummy_service

    def test_get_nonexistent(self):
        assert registry.get("nonexistent") is None

    def test_overwrite_service(self):
        s1 = "first"
        s2 = "second"
        registry.register("overwrite", s1)
        assert registry.get("overwrite") == s1
        registry.register("overwrite", s2)
        assert registry.get("overwrite") == s2
