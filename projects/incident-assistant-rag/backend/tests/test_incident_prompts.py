"""Edge cases for IncidentPromptBuilder."""

import pytest

from app.reasoning.incident_prompts import IncidentPromptBuilder
from app.schemas.search_schema import SearchResult


def test_incident_prompt_rejects_blank_description():
    with pytest.raises(ValueError, match="cannot be empty"):
        IncidentPromptBuilder().build("", "High", [], None, None)


def test_incident_prompt_rejects_whitespace_only_description():
    with pytest.raises(ValueError, match="cannot be empty"):
        IncidentPromptBuilder().build("   \t  ", "High", [], None, None)


def test_incident_prompt_includes_chunks_when_provided():
    chunks = [
        SearchResult(chunk_id="1", source_file="runbook.md", chunk_index=0, text="Check logs.", score=0.88),
    ]
    prompt = IncidentPromptBuilder().build("Pods crash-loop after deploy", "High", chunks, "api", "prod")
    assert "runbook.md" in prompt
    assert "Check logs." in prompt
    assert "api" in prompt


def test_incident_prompt_contains_no_context_line_when_chunks_empty():
    prompt = IncidentPromptBuilder().build("Something is broken in staging", "Medium", [], None, "staging")
    assert "No relevant context was retrieved" in prompt


def test_incident_prompt_includes_severity_placeholder():
    prompt = IncidentPromptBuilder().build("Network blips affecting users", "Critical", [])
    assert "Critical" in prompt
