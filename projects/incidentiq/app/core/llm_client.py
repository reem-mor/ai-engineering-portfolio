"""Async LLM clients with OpenAI primary and Gemini fallback on transient failures.

The chain is exposed as a process-wide singleton via ``get_llm_client()``. OpenAI
is tried first with exponential backoff; when all retries are exhausted and
``GEMINI_API_KEY`` is configured, Gemini is invoked automatically.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from threading import Lock

from google import genai
from google.genai import types as genai_types
from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
    RateLimitError,
)

from app.config import get_settings
from app.utils.logger import get_logger

_MAX_ATTEMPTS: int = 3
_BACKOFF_BASE_SECONDS: float = 1.0
_USER_PROMPT_LOG_LIMIT: int = 50

_RETRYABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)


@dataclass(frozen=True, slots=True)
class LLMResult:
    """Text completion plus the model identifier that produced it."""

    text: str
    model_used: str


class OpenAIClient:
    """Async OpenAI chat-completions client with bounded retries."""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key_required,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.logger = get_logger(__name__)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        prompt_preview = _truncate(user_prompt, _USER_PROMPT_LOG_LIMIT)
        last_error: BaseException | None = None

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=self.max_tokens,
                )
            except _RETRYABLE_EXCEPTIONS as exc:
                last_error = exc
                self.logger.warning(
                    "OpenAI retryable error: attempt=%d/%d error_type=%s message=%s",
                    attempt,
                    _MAX_ATTEMPTS,
                    type(exc).__name__,
                    str(exc),
                )
                if attempt == _MAX_ATTEMPTS:
                    break
                await asyncio.sleep(_BACKOFF_BASE_SECONDS * (2 ** (attempt - 1)))
                continue
            except APIError as exc:
                self.logger.error(
                    "OpenAI non-retryable API error: error_type=%s message=%s",
                    type(exc).__name__,
                    str(exc),
                )
                raise RuntimeError(
                    f"OpenAI API error ({type(exc).__name__}): {exc}"
                ) from exc

            choices = getattr(response, "choices", None) or []
            if not choices or choices[0].message is None or choices[0].message.content is None:
                raise RuntimeError("OpenAI returned an empty response with no choices.")

            content = choices[0].message.content
            usage = getattr(response, "usage", None)
            prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
            self.logger.info(
                "OpenAI success: model=%s attempt=%d prompt_tokens=%d completion_tokens=%d prompt_preview=%r",
                self.model,
                attempt,
                prompt_tokens,
                completion_tokens,
                prompt_preview,
            )
            return content

        raise RuntimeError(
            f"OpenAI request failed after {_MAX_ATTEMPTS} attempts "
            f"(last error: {type(last_error).__name__ if last_error else 'unknown'}: {last_error})"
        ) from last_error


class GeminiClient:
    """Google Gemini client used as the fallback LLM provider."""

    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.GEMINI_MODEL
        self.max_tokens = settings.MAX_TOKENS
        self.logger = get_logger(__name__)
        self._client = genai.Client(api_key=settings.gemini_api_key_required)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> str:
        prompt = f"{system_prompt}\n\n{user_prompt}"
        prompt_preview = _truncate(user_prompt, _USER_PROMPT_LOG_LIMIT)

        def _call() -> str:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=self.max_tokens,
                ),
            )
            text = getattr(response, "text", None)
            if not text or not str(text).strip():
                raise RuntimeError("Gemini returned an empty response.")
            return str(text).strip()

        try:
            content = await asyncio.to_thread(_call)
        except Exception as exc:
            self.logger.error(
                "Gemini generation failed: model=%s error_type=%s message=%s",
                self.model,
                type(exc).__name__,
                str(exc),
            )
            raise RuntimeError(
                f"Gemini API error ({type(exc).__name__}): {exc}"
            ) from exc

        self.logger.info(
            "Gemini success: model=%s prompt_preview=%r",
            self.model,
            prompt_preview,
        )
        return content


class LLMChain:
    """Try OpenAI first; fall back to Gemini on exhausted transient OpenAI failures."""

    def __init__(self) -> None:
        settings = get_settings()
        self._openai = OpenAIClient()
        self._settings = settings
        self._logger = get_logger(__name__)
        self._gemini: GeminiClient | None = None
        if settings.llm_fallback_available:
            self._gemini = GeminiClient()
        self._logger.info(
            "LLM chain initialized: primary=%s fallback=%s fallback_enabled=%s",
            settings.OPENAI_MODEL,
            settings.GEMINI_MODEL if self._gemini else "none",
            settings.llm_fallback_available,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> LLMResult:
        try:
            text = await self._openai.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            return LLMResult(text=text, model_used=self._settings.OPENAI_MODEL)
        except RuntimeError as exc:
            if not self._settings.LLM_FALLBACK_ENABLED or self._gemini is None:
                raise
            self._logger.warning(
                "LLM fallback triggered: primary=openai fallback=gemini reason=%s",
                str(exc),
            )
            text = await self._gemini.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            return LLMResult(text=text, model_used=self._settings.GEMINI_MODEL)


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


_llm_client_instance: LLMChain | None = None
_llm_client_lock: Lock = Lock()


def get_llm_client() -> LLMChain:
    """Return the singleton LLM chain, constructing it on first access."""
    global _llm_client_instance
    if _llm_client_instance is None:
        with _llm_client_lock:
            if _llm_client_instance is None:
                _llm_client_instance = LLMChain()
    return _llm_client_instance
