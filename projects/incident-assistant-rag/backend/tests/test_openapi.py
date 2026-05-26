"""FastAPI wiring and OpenAPI surface."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_schema_available():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["openapi"].startswith("3.")
    paths = data.get("paths", {})
    assert "/api/health" in paths


def test_swagger_docs_ui_available():
    response = client.get("/docs")
    assert response.status_code == 200
    text = response.text.lower()
    assert "swagger" in text or "openapi" in text


def test_root_path_returns_404_until_defined():
    assert client.get("/").status_code == 404

