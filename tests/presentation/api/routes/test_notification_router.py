import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from main import app
from src.presentation.api.dependencies import get_event_bus


@pytest.mark.NotificationRouter
class TestNotificationRouter:
    @pytest.fixture
    def mock_event_bus(self):
        mock = MagicMock()
        app.dependency_overrides[get_event_bus] = lambda: mock
        yield mock
        app.dependency_overrides.pop(get_event_bus, None)

    def test_events_stream(self, mock_event_bus):
        # Mock subscribe to yield a few messages then stop
        mock_event_bus.subscribe.return_value = [
            {"job_id": "1", "status": "processing"},
            {"job_id": "1", "status": "completed"},
        ]

        client = TestClient(app)

        # In TestClient, SSE might be tricky if it blocks.
        # But for mock generators it should work or we can test the generator directly.
        # Let's try the request first.
        with client.stream("GET", "/rest/notifications/events") as response:
            assert response.status_code == 200
            # TestClient.stream might not be enough for standard SSE testing in all environments
            # but it should at least trigger the generator.

            # Since we are using EventSourceResponse, it returns a stream.
            # Let's check if we can read lines.
            lines = list(response.iter_lines())
            assert len(lines) > 0

            # Check for established message
            assert any("connected" in line for line in lines)
            assert any("processing" in line for line in lines)
            assert any("completed" in line for line in lines)

    def test_events_stream_exception(self, mock_event_bus):
        mock_event_bus.subscribe.side_effect = Exception("Redis connection error")

        client = TestClient(app)
        with client.stream("GET", "/rest/notifications/events") as response:
            lines = list(response.iter_lines())
            assert any("error" in line for line in lines)
            assert any("Redis connection error" in line for line in lines)
