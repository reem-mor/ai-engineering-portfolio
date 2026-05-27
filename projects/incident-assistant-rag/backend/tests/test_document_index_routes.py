"""API tests for document indexing endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.rag.embeddings import FakeEmbeddingProvider

client = TestClient(app)


def test_index_samples_builds_faiss_index(tmp_path, monkeypatch):
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    (samples_dir / "runbook.txt").write_text(
        "payment-service timeout and queue backlog investigation steps." * 6,
        encoding="utf-8",
    )
    index_dir = tmp_path / "faiss_index"
    monkeypatch.setattr(settings, "sample_documents_dir", samples_dir)
    monkeypatch.setattr(settings, "faiss_index_dir", index_dir)

    with patch(
        "app.api.document_routes.OpenAIEmbeddingProvider",
        lambda: FakeEmbeddingProvider(dimensions=8),
    ):
        response = client.post("/api/documents/index-samples")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["indexed_file_count"] == 1
    assert "runbook.txt" in body["indexed_files"]
    assert (index_dir / settings.faiss_index_file).is_file()
    assert (index_dir / settings.faiss_metadata_file).is_file()


def test_index_samples_returns_400_when_no_documents(tmp_path, monkeypatch):
    empty_dir = tmp_path / "empty_samples"
    empty_dir.mkdir()
    monkeypatch.setattr(settings, "sample_documents_dir", empty_dir)

    response = client.post("/api/documents/index-samples")

    assert response.status_code == 400
    assert "No sample documents" in response.json()["detail"]


def test_index_uploaded_builds_faiss_index(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "uploaded.md").write_text(
        "# Uploaded runbook\nMonitor API gateway 5xx errors and rollback if needed." * 4,
        encoding="utf-8",
    )
    index_dir = tmp_path / "faiss_index"
    monkeypatch.setattr(settings, "raw_data_dir", raw_dir)
    monkeypatch.setattr(settings, "faiss_index_dir", index_dir)

    with patch(
        "app.api.document_routes.OpenAIEmbeddingProvider",
        lambda: FakeEmbeddingProvider(dimensions=8),
    ):
        response = client.post("/api/documents/index-uploaded")

    assert response.status_code == 200
    body = response.json()
    assert body["indexed_file_count"] == 1
    assert "uploaded.md" in body["indexed_files"]


def test_index_uploaded_returns_400_when_no_uploads(tmp_path, monkeypatch):
    empty_raw = tmp_path / "empty_raw"
    empty_raw.mkdir()
    monkeypatch.setattr(settings, "raw_data_dir", empty_raw)

    response = client.post("/api/documents/index-uploaded")

    assert response.status_code == 400
    assert "No uploaded documents" in response.json()["detail"]
