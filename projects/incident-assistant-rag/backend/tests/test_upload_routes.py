from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_rejects_unsupported_file_type():
    response = client.post("/api/upload", files={"file": ("malware.exe", BytesIO(b"bad"), "application/octet-stream")})
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_rejects_empty_file():
    response = client.post("/api/upload", files={"file": ("empty.txt", BytesIO(b""), "text/plain")})
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_accepts_text_file():
    response = client.post("/api/upload", files={"file": ("runbook.txt", BytesIO(b"hello incident"), "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "runbook.txt"
    assert data["status"] == "uploaded"


def test_upload_rejects_file_without_extension():
    response = client.post("/api/upload", files={"file": ("README", BytesIO(b"content"), "text/plain")})
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
