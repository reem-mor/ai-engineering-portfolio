"""API integration tests for chat with a built FAISS index (fake embeddings)."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.rag.embeddings import FakeEmbeddingProvider
from app.rag.faiss_store import FaissVectorStore
from app.rag.generator import FakeAnswerGenerator
from app.rag.rag_pipeline import RAGPipeline
from app.rag.retriever import Retriever
from app.services.document_service import DocumentService

client = TestClient(app)
FAKE_DIM = 8


def _build_index_from_samples(tmp_path, monkeypatch) -> None:
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    (samples_dir / "auth_runbook.txt").write_text(
        "auth-service login failure after deployment. Check logs, health endpoint, and environment variables."
        * 8,
        encoding="utf-8",
    )
    index_dir = tmp_path / "faiss_index"
    monkeypatch.setattr(settings, "sample_documents_dir", samples_dir)
    monkeypatch.setattr(settings, "faiss_index_dir", index_dir)

    service = DocumentService(
        embedding_provider=FakeEmbeddingProvider(dimensions=FAKE_DIM),
        vector_store=FaissVectorStore(index_dir=index_dir),
    )
    files = service.list_supported_files(samples_dir)
    service.process_embed_and_index_files(files)


def test_chat_returns_grounded_response_when_index_exists(tmp_path, monkeypatch):
    _build_index_from_samples(tmp_path, monkeypatch)
    index_dir = tmp_path / "faiss_index"

    pipeline = RAGPipeline(
        retriever=Retriever(
            vector_store=FaissVectorStore(index_dir=index_dir),
            embedding_provider=FakeEmbeddingProvider(dimensions=FAKE_DIM),
        ),
        answer_generator=FakeAnswerGenerator(),
        score_threshold=0.0,
    )

    with patch("app.api.chat_routes.RAGPipeline.create_default", return_value=pipeline):
        response = client.post(
            "/api/chat",
            json={"question": "What should I check when users cannot log in after deployment?", "top_k": 3},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["used_context"] is True
    assert body["sources"]
    assert body["answer"]
    assert body["confidence"] in {"high", "medium", "low"}


def test_chat_returns_400_when_faiss_index_missing(tmp_path, monkeypatch):
    empty_index_dir = tmp_path / "empty_faiss"
    empty_index_dir.mkdir()
    monkeypatch.setattr(settings, "faiss_index_dir", empty_index_dir)

    response = client.post(
        "/api/chat",
        json={"question": "What should I check?", "top_k": 3},
    )

    assert response.status_code == 400
    assert "FAISS index" in response.json()["detail"]
