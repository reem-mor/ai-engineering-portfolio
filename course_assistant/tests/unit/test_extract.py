"""Unit tests for content extraction."""

from __future__ import annotations

from course_assistant.rag.extract import extract_text, is_extractable
from tests.fixtures.docs import make_docx


def test_is_extractable() -> None:
    assert is_extractable("Python-intro-hw.docx")
    assert is_extractable("lecture2.pdf")
    assert is_extractable("agent.py")
    assert not is_extractable("part 1.mp4")
    assert not is_extractable("archive.zip")


def test_extract_docx() -> None:
    data = make_docx(["First paragraph about Python.", "Second about loops."])
    text = extract_text("hw.docx", data)
    assert "First paragraph about Python." in text
    assert "Second about loops." in text


def test_extract_plaintext_and_code() -> None:
    assert extract_text("notes.txt", b"hello world") == "hello world"
    assert "def main" in extract_text("agent.py", b"def main():\n    pass\n")


def test_unknown_type_returns_empty() -> None:
    assert extract_text("clip.mp4", b"\x00\x01\x02") == ""
