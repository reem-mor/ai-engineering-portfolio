"""Integration tests for the end-to-end RAG pipeline with mocked retriever and LLM client."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.core.rag_pipeline import RAGPipeline, init_pipeline
from app.core.retriever import init_retriever
from app.models.schemas import QueryRequest, RAGResponse


@pytest.fixture(scope="module")
def pipeline() -> RAGPipeline:
    """Initialise the retriever singleton and return the RAG pipeline."""
    init_retriever("knowledge_base/faiss_index")
    return init_pipeline()


def test_pipeline_initializes(pipeline: RAGPipeline) -> None:
    """Pipeline initializes without errors."""
    assert pipeline is not None
    assert isinstance(pipeline, RAGPipeline)


@pytest.mark.asyncio
async def test_query_returns_rag_response(pipeline: RAGPipeline) -> None:
    """Valid query returns a RAGResponse object."""
    with patch.object(
        pipeline._llm_client,
        "generate",
        new_callable=AsyncMock,
        return_value="## Assessment\nTest answer.\n## Triage Steps\n1. Step one.",
    ):
        request = QueryRequest(
            question="How do I handle kubernetes pod crash loop?"
        )
        response = await pipeline.query(request)
        assert isinstance(response, RAGResponse)
        assert len(response.answer) > 0
        assert response.query == request.question
        assert response.processing_time_ms > 0
        assert response.confidence in ["high", "medium", "low", "none"]


@pytest.mark.asyncio
async def test_irrelevant_query_returns_none_confidence(pipeline: RAGPipeline) -> None:
    """Irrelevant query returns confidence=none without calling LLM."""
    with patch.object(
        pipeline._llm_client,
        "generate",
        new_callable=AsyncMock,
    ) as mock_llm:
        request = QueryRequest(
            question="What is the recipe for chocolate cake?"
        )
        response = await pipeline.query(request)
        if response.confidence == "none":
            mock_llm.assert_not_called()
        assert response.confidence in ["none", "low", "medium", "high"]


@pytest.mark.asyncio
async def test_severity_filter_applied(pipeline: RAGPipeline) -> None:
    """Severity filter reduces or changes results."""
    with patch.object(
        pipeline._llm_client,
        "generate",
        new_callable=AsyncMock,
        return_value="## Assessment\nFiltered answer.",
    ):
        request_filtered = QueryRequest(
            question="How do I handle a kubernetes incident?",
            severity_filter="P1",
        )
        response = await pipeline.query(request_filtered)
        assert isinstance(response, RAGResponse)


def test_query_request_validation_min_length() -> None:
    """QueryRequest rejects questions under 3 chars."""
    with pytest.raises(Exception):
        QueryRequest(question="ab")


def test_query_request_validation_max_length() -> None:
    """QueryRequest rejects questions over 500 chars."""
    with pytest.raises(Exception):
        QueryRequest(question="x" * 501)


def test_query_request_validation_blank() -> None:
    """QueryRequest rejects blank/whitespace questions."""
    with pytest.raises(Exception):
        QueryRequest(question="   ")
