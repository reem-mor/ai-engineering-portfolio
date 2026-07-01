"""Tests for hw07 system prompt."""

from __future__ import annotations

from prompts import load_system_prompt


def test_system_prompt_loads() -> None:
    text = load_system_prompt()
    assert "CVE Intelligence Dataset" in text or "CVE Intelligence" in text
    assert "lookup_cve" in text
    assert "Not found in the CVE Intelligence dataset" in text


def test_system_prompt_covers_routing() -> None:
    text = load_system_prompt()
    assert "historical" in text.lower() or "dataset" in text.lower()
    assert "EPSS" in text or "KEV" in text
    assert "search_cves" in text
