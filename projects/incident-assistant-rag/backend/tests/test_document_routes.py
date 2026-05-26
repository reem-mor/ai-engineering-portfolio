from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_sample_documents_returns_files():
    response = client.get("/api/documents/samples")
    assert response.status_code == 200
    assert "files" in response.json()
