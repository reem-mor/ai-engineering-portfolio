"""Tests for the hw07 system prompt."""

from __future__ import annotations

from prompts import load_system_prompt


def test_system_prompt_loads() -> None:
    text = load_system_prompt()
    assert "AI Job Market Intelligence Assistant" in text
    assert "Knowledge Base" in text
    assert "live job-search tool" in text


def test_system_prompt_covers_routing_and_grounding() -> None:
    text = load_system_prompt()
    assert "Kaggle dataset" in text
    assert "RapidAPI" in text
    assert "Do not invent" in text
    assert "If the tool fails" in text
