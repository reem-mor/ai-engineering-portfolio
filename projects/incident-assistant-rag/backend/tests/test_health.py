from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok_status():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database_enabled" in data


def test_health_payload_includes_service_metadata():
    response = client.get("/api/health")
    data = response.json()
    for key in ("status", "service", "version", "environment", "database_enabled"):
        assert key in data
