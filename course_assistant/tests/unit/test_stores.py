"""Tests for the vector-store backends (InMemory + Chroma) via a fake embedder."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from course_assistant.rag.embeddings import Embedder, HashingEmbedder
from course_assistant.rag.stores import ChromaVectorStore, InMemoryVectorStore
from course_assistant.rag.vectorstore import Document, VectorStore

StoreFactory = Callable[[Embedder], VectorStore]

_STORES: list[StoreFactory] = [
    lambda e: InMemoryVectorStore(e),
    lambda e: ChromaVectorStore(e, persist_dir=None),  # ephemeral
]

_DOCS = [
    Document("1", "python loops functions and variables", "Python-intro-hw.docx", {"lesson": "2"}),
    Document("2", "docker containers nginx and ec2 deployment", "Ubuntu.docx", {"lesson": "7"}),
    Document(
        "3",
        "bedrock agent retrieval augmented generation",
        "bedroc_agent.py",
        {"lesson": "10"},
    ),
]


@pytest.mark.parametrize("make_store", _STORES)
def test_search_ranks_relevant_doc_first(make_store: StoreFactory) -> None:
    store = make_store(HashingEmbedder(dim=128))
    store.add(_DOCS)
    results = store.search("how do docker containers and nginx work", k=1)
    assert len(results) == 1
    assert results[0].document.id == "2"
    assert results[0].document.source == "Ubuntu.docx"
    assert results[0].document.metadata["lesson"] == "7"


@pytest.mark.parametrize("make_store", _STORES)
def test_search_returns_k_results(make_store: StoreFactory) -> None:
    store = make_store(HashingEmbedder(dim=128))
    store.add(_DOCS)
    assert len(store.search("python and docker and bedrock", k=3)) == 3


@pytest.mark.parametrize("make_store", _STORES)
def test_clear_empties_the_store(make_store: StoreFactory) -> None:
    store = make_store(HashingEmbedder(dim=128))
    store.add(_DOCS)
    store.clear()
    assert store.search("anything", k=3) == []
