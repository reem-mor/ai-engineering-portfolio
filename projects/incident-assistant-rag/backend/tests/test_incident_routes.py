from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_incident_rejects_short_description():
    response = client.post("/api/incident/analyze", json={"description": "short", "top_k": 3})
    assert response.status_code == 422


def test_incident_rejects_invalid_top_k():
    response = client.post("/api/incident/analyze", json={"description": "Many users cannot log in", "top_k": 0})
    assert response.status_code == 422


def test_incident_rejects_top_k_above_schema_max():
    response = client.post(
        "/api/incident/analyze",
        json={"description": "This incident has enough chars", "top_k": 11},
    )
    assert response.status_code == 422
