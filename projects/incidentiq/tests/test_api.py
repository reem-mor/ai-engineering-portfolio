"""HTTP-level tests for FastAPI routes using TestClient — covers /query and /health."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import RAGResponse


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    """Yield a TestClient with the FastAPI lifespan active (loads FAISS once)."""
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client: TestClient) -> None:
    """GET /health returns 200 with correct schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "faiss_index_loaded" in data
    assert "total_documents_indexed" in data
    assert "embedding_model" in data
    assert "llm_model" in data
    assert "version" in data


def test_query_endpoint_valid(client: TestClient) -> None:
    """POST /api/query returns 200 with RAGResponse schema."""
    mock_response = RAGResponse(
        answer="## Assessment\nTest answer.",
        sources=[],
        retrieved_count=0,
        confidence="none",
        query="test question here",
        processing_time_ms=100,
        model_used="gpt-4o-mini",
    )
    with patch("app.api.routes.query.get_pipeline") as mock_get_pipeline:
        mock_pipeline = MagicMock()
        mock_pipeline.query = AsyncMock(return_value=mock_response)
        mock_get_pipeline.return_value = mock_pipeline

        response = client.post(
            "/api/query",
            json={"question": "How do I handle a kubernetes pod crash?"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data
        assert "processing_time_ms" in data


def test_query_endpoint_too_short(client: TestClient) -> None:
    """POST /api/query with short question returns 422."""
    response = client.post("/api/query", json={"question": "ab"})
    assert response.status_code == 422


def test_query_endpoint_too_long(client: TestClient) -> None:
    """POST /api/query with 501+ char question returns 422."""
    response = client.post("/api/query", json={"question": "x" * 501})
    assert response.status_code == 422


def test_query_endpoint_missing_body(client: TestClient) -> None:
    """POST /api/query with no body returns 422."""
    response = client.post("/api/query")
    assert response.status_code == 422


def test_processing_time_header(client: TestClient) -> None:
    """POST /api/query response includes X-Processing-Time header."""
    mock_response = RAGResponse(
        answer="Test answer.",
        sources=[],
        retrieved_count=0,
        confidence="none",
        query="test question here",
        processing_time_ms=100,
        model_used="gpt-4o-mini",
    )
    with patch("app.api.routes.query.get_pipeline") as mock_get_pipeline:
        mock_pipeline = MagicMock()
        mock_pipeline.query = AsyncMock(return_value=mock_response)
        mock_get_pipeline.return_value = mock_pipeline

        response = client.post(
            "/api/query",
            json={"question": "How do I handle a kubernetes pod crash?"},
        )
        assert "x-processing-time" in response.headers


def test_root_endpoint(client: TestClient) -> None:
    """GET / returns 200."""
    response = client.get("/")
    assert response.status_code == 200
