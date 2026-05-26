from pathlib import Path

import pytest

from app.rag.faiss_store import FaissVectorStore
from app.schemas.chunk_schema import DocumentChunk
from app.schemas.embedding_schema import EmbeddedChunk


def make_embedded_chunks():
    return [
        EmbeddedChunk(chunk=DocumentChunk(chunk_id="a::0", source_file="a.md", chunk_index=0, text="auth login"), embedding=[1.0, 0.0, 0.0]),
        EmbeddedChunk(chunk=DocumentChunk(chunk_id="b::0", source_file="b.md", chunk_index=0, text="payment timeout"), embedding=[0.0, 1.0, 0.0]),
    ]


def test_faiss_store_build_save_load_search(tmp_path: Path):
    store = FaissVectorStore(index_dir=tmp_path)
    store.build_and_save(make_embedded_chunks())
    loaded = FaissVectorStore(index_dir=tmp_path)
    loaded.load()
    results = loaded.search([1.0, 0.0, 0.0], top_k=1)
    assert results[0].source_file == "a.md"


def test_faiss_store_rejects_dimension_mismatch(tmp_path: Path):
    store = FaissVectorStore(index_dir=tmp_path)
    store.build_index(make_embedded_chunks())
    with pytest.raises(ValueError, match="does not match index dimension"):
        store.search([1.0, 0.0], top_k=1)


def test_faiss_store_rejects_empty_embedded_chunks(tmp_path: Path):
    store = FaissVectorStore(index_dir=tmp_path)
    with pytest.raises(ValueError, match="No embedded chunks"):
        store.build_index([])


def test_faiss_store_rejects_zero_embedding_dimension(tmp_path: Path):
    chunk = DocumentChunk(chunk_id="z::0", source_file="z.md", chunk_index=0, text="hello")
    store = FaissVectorStore(index_dir=tmp_path)
    with pytest.raises(ValueError, match="Embedding dimension"):
        store.build_index([EmbeddedChunk(chunk=chunk, embedding=[])])


def test_faiss_store_rejects_mixed_embedding_dimensions(tmp_path: Path):
    a = EmbeddedChunk(chunk=DocumentChunk(chunk_id="a::0", source_file="a.md", chunk_index=0, text="a"), embedding=[1.0, 0.0])
    b = EmbeddedChunk(chunk=DocumentChunk(chunk_id="b::0", source_file="b.md", chunk_index=0, text="b"), embedding=[1.0, 0.0, 0.0])
    store = FaissVectorStore(index_dir=tmp_path)
    with pytest.raises(ValueError, match="same dimension"):
        store.build_index([a, b])


def test_faiss_store_search_rejects_non_positive_top_k(tmp_path: Path):
    store = FaissVectorStore(index_dir=tmp_path)
    store.build_index(make_embedded_chunks())
    with pytest.raises(ValueError, match="top_k must be positive"):
        store.search([1.0, 0.0, 0.0], top_k=0)


def test_faiss_store_save_without_build_raises(tmp_path: Path):
    store = FaissVectorStore(index_dir=tmp_path)
    with pytest.raises(ValueError, match="empty"):
        store.save()
