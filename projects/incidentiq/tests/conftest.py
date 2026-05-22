"""Shared pytest configuration for deterministic, secret-free test runs."""

from __future__ import annotations

import os


def pytest_configure() -> None:
    """Provide safe placeholder credentials before application modules import."""
    os.environ.setdefault("OPENAI_API_KEY", "test-openai-api-key")
    os.environ.setdefault("GEMINI_API_KEY", "your_gemini_api_key_here")
    os.environ.setdefault("LLM_FALLBACK_ENABLED", "false")
