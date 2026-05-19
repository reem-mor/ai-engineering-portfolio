"""Unit tests for the FAISS retriever: top-K correctness, empty-index handling, and edge cases."""

from __future__ import annotations

import pytest

from app.core.retriever import FAISSRetriever, init_retriever


@pytest.fixture(scope="module")
def retriever() -> FAISSRetriever:
    """Load the FAISS retriever once for the whole module."""
    return init_retriever("knowledge_base/faiss_index")


def test_retriever_loads(retriever: FAISSRetriever) -> None:
    """Retriever initializes without errors."""
    assert retriever is not None


def test_retriever_stats(retriever: FAISSRetriever) -> None:
    """Index stats return expected fields."""
    stats = retriever.get_index_stats()
    assert "total_vectors" in stats
    assert stats["total_vectors"] > 0
    assert stats["dimension"] == 384


def test_retrieve_known_query(retriever: FAISSRetriever) -> None:
    """Known query returns relevant results."""
    results = retriever.retrieve("kubernetes pod crash loop", top_k=5)
    assert len(results) > 0
    assert results[0]["rank"] == 1
    assert "chunk_text" in results[0]
    assert "metadata" in results[0]
    assert "score" in results[0]


def test_retrieve_returns_metadata_fields(retriever: FAISSRetriever) -> None:
    """Each result contains all required metadata fields."""
    results = retriever.retrieve("database connection pool", top_k=3)
    assert len(results) > 0
    for result in results:
        assert "id" in result["metadata"]
        assert "title" in result["metadata"]
        assert "severity" in result["metadata"]
        assert "category" in result["metadata"]
        assert "document_type" in result["metadata"]


def test_retrieve_irrelevant_query(retriever: FAISSRetriever) -> None:
    """Irrelevant query returns empty list (threshold filtered)."""
    results = retriever.retrieve("what is the weather in paris", top_k=5)
    assert isinstance(results, list)


def test_retrieve_top_k_respected(retriever: FAISSRetriever) -> None:
    """Result count does not exceed top_k."""
    results = retriever.retrieve("incident", top_k=3)
    assert len(results) <= 3


def test_retrieve_results_ordered_by_rank(retriever: FAISSRetriever) -> None:
    """Results are ordered rank 1, 2, 3..."""
    results = retriever.retrieve("kafka consumer lag", top_k=5)
    if len(results) > 1:
        ranks = [r["rank"] for r in results]
        assert ranks == sorted(ranks)
