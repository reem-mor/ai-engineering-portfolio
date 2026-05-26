import pytest

from app.rag.chunker import TextChunker


def test_chunker_creates_chunks():
    chunker = TextChunker(chunk_size=40, chunk_overlap=5)
    chunks = chunker.chunk("a" * 120, "test.txt")
    assert len(chunks) > 1
    assert chunks[0].source_file == "test.txt"


def test_chunker_rejects_bad_overlap():
    with pytest.raises(ValueError):
        TextChunker(chunk_size=10, chunk_overlap=10)


def test_chunker_rejects_negative_overlap():
    with pytest.raises(ValueError, match="overlap cannot be negative"):
        TextChunker(chunk_size=40, chunk_overlap=-1)


def test_chunker_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        TextChunker(chunk_size=0, chunk_overlap=0)


def test_chunker_produces_single_chunk_for_short_text():
    chunker = TextChunker(chunk_size=200, chunk_overlap=10)
    chunks = chunker.chunk("hello world", "tiny.md")
    assert len(chunks) == 1
    assert chunks[0].text == "hello world"
