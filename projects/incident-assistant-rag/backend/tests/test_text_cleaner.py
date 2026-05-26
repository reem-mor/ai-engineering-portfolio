import pytest
from app.rag.text_cleaner import TextCleaner


def test_cleaner_normalizes_whitespace():
    assert TextCleaner().clean("hello   world\n\n\nnext") == "hello world\n\nnext"


def test_cleaner_rejects_empty():
    with pytest.raises(ValueError):
        TextCleaner().clean(" ")


def test_cleaner_preserves_intentional_blank_line_between_sections():
    out = TextCleaner().clean("lineOne\n\nlineThree")
    assert "lineOne" in out
    assert "lineThree" in out
