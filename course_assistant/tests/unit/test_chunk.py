"""Unit tests for the text chunker."""

from __future__ import annotations

import pytest

from course_assistant.rag.chunk import chunk_text


def test_empty_text_yields_no_chunks() -> None:
    assert chunk_text("   \n\t  ") == []


def test_short_text_is_single_chunk_and_whitespace_collapsed() -> None:
    assert chunk_text("hello   world\n\nagain") == ["hello world again"]


def test_long_text_splits_into_multiple_chunks() -> None:
    text = " ".join(f"word{i}" for i in range(400))
    chunks = chunk_text(text, chunk_size=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_chunks_overlap_and_dont_split_words() -> None:
    text = " ".join(f"token{i:03d}" for i in range(100))
    chunks = chunk_text(text, chunk_size=120, overlap=30)
    # No chunk starts or ends mid-token.
    for c in chunks:
        assert not c.startswith("oken")
        assert "  " not in c
    # Consecutive chunks share some trailing/leading tokens (overlap).
    first_tail = set(chunks[0].split()[-3:])
    second_head = set(chunks[1].split()[:5])
    assert first_tail & second_head


def test_invalid_params_raise() -> None:
    with pytest.raises(ValueError):
        chunk_text("x", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("x", chunk_size=100, overlap=100)
