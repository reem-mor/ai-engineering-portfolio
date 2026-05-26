from pathlib import Path

import pytest

from app.rag.embeddings import FakeEmbeddingProvider
from app.rag.faiss_store import FaissVectorStore
from app.rag.retriever import Retriever
from app.schemas.chunk_schema import DocumentChunk
from app.schemas.embedding_schema import EmbeddedChunk


def build_store(tmp_path: Path) -> FaissVectorStore:
    provider = FakeEmbeddingProvider(dimensions=8)
    chunk = DocumentChunk(chunk_id="auth::0", source_file="auth.md", chunk_index=0, text="auth login deployment")
    store = FaissVectorStore(index_dir=tmp_path)
    store.build_and_save([EmbeddedChunk(chunk=chunk, embedding=provider.embed_text(chunk.text))])
    loaded = FaissVectorStore(index_dir=tmp_path)
    loaded.load()
    return loaded


def test_retriever_returns_results(tmp_path: Path):
    provider = FakeEmbeddingProvider(dimensions=8)
    retriever = Retriever(vector_store=build_store(tmp_path), embedding_provider=provider)
    results = retriever.retrieve("auth login", top_k=1)
    assert results[0].source_file == "auth.md"


def test_retriever_rejects_empty_question(tmp_path: Path):
    provider = FakeEmbeddingProvider(dimensions=8)
    retriever = Retriever(vector_store=build_store(tmp_path), embedding_provider=provider)
    with pytest.raises(ValueError):
        retriever.retrieve(" ")


def test_retriever_rejects_zero_top_k(tmp_path: Path):
    provider = FakeEmbeddingProvider(dimensions=8)
    retriever = Retriever(vector_store=build_store(tmp_path), embedding_provider=provider)
    with pytest.raises(ValueError, match="top_k must be positive"):
        retriever.retrieve("auth", top_k=0)


def test_retriever_rejects_negative_top_k(tmp_path: Path):
    provider = FakeEmbeddingProvider(dimensions=8)
    retriever = Retriever(vector_store=build_store(tmp_path), embedding_provider=provider)
    with pytest.raises(ValueError, match="top_k must be positive"):
        retriever.retrieve("auth", top_k=-1)
