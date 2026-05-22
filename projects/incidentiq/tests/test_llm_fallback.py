"""Tests for OpenAI primary + Gemini fallback LLM chain."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.llm_client import LLMChain, LLMResult


@pytest.mark.asyncio
async def test_openai_success_does_not_call_gemini() -> None:
    chain = LLMChain.__new__(LLMChain)
    chain._settings = MagicMock()
    chain._settings.OPENAI_MODEL = "gpt-4o-mini"
    chain._settings.GEMINI_MODEL = "gemini-2.0-flash"
    chain._settings.LLM_FALLBACK_ENABLED = True
    chain._openai = MagicMock()
    chain._openai.generate = AsyncMock(return_value="primary answer")
    chain._gemini = MagicMock()
    chain._gemini.generate = AsyncMock(return_value="fallback answer")
    chain._logger = MagicMock()

    result = await chain.generate("system", "user")

    assert result == LLMResult(text="primary answer", model_used="gpt-4o-mini")
    chain._gemini.generate.assert_not_called()


@pytest.mark.asyncio
async def test_openai_failure_falls_back_to_gemini() -> None:
    chain = LLMChain.__new__(LLMChain)
    chain._settings = MagicMock()
    chain._settings.OPENAI_MODEL = "gpt-4o-mini"
    chain._settings.GEMINI_MODEL = "gemini-2.0-flash"
    chain._settings.LLM_FALLBACK_ENABLED = True
    chain._openai = MagicMock()
    chain._openai.generate = AsyncMock(
        side_effect=RuntimeError("OpenAI request failed after 3 attempts")
    )
    chain._gemini = MagicMock()
    chain._gemini.generate = AsyncMock(return_value="fallback answer")
    chain._logger = MagicMock()

    result = await chain.generate("system", "user")

    assert result == LLMResult(text="fallback answer", model_used="gemini-2.0-flash")
    chain._gemini.generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_openai_failure_without_gemini_reraises() -> None:
    chain = LLMChain.__new__(LLMChain)
    chain._settings = MagicMock()
    chain._settings.LLM_FALLBACK_ENABLED = False
    chain._openai = MagicMock()
    chain._openai.generate = AsyncMock(side_effect=RuntimeError("OpenAI down"))
    chain._gemini = None
    chain._logger = MagicMock()

    with pytest.raises(RuntimeError, match="OpenAI down"):
        await chain.generate("system", "user")
