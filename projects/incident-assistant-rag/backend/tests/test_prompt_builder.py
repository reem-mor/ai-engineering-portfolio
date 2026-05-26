import pytest

from app.rag.prompt_builder import PromptBuilder
from app.schemas.search_schema import SearchResult


def test_prompt_builder_includes_context():
    prompt = PromptBuilder().build("What to check?", [SearchResult(chunk_id="a", source_file="auth.md", chunk_index=0, text="Check logs", score=0.9)])
    assert "Check logs" in prompt
    assert "Do not invent" in prompt


def test_prompt_builder_no_context():
    prompt = PromptBuilder().build("Unknown question", [])
    assert "did not return relevant context" in prompt


def test_prompt_builder_rejects_empty_question():
    with pytest.raises(ValueError):
        PromptBuilder().build(" ", [])
