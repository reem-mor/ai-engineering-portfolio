"""Tests for hw07 prompt loading."""

from __future__ import annotations

from prompts import load_system_prompt


def test_system_prompt_loads_without_io_contract() -> None:
    prompt = load_system_prompt()
    assert "search_live_jobs" in prompt
    assert "#ai-job-postings" in prompt
    assert "I/O contract" not in prompt


def test_system_prompt_can_include_io_contract() -> None:
    prompt = load_system_prompt(include_io_contract=True)
    assert "I/O contract" in prompt
