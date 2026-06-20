"""Embedding backends behind a small :class:`Embedder` interface.

- :class:`OpenAIEmbedder` — production embeddings (lazy client; no paid calls in
  tests).
- :class:`HashingEmbedder` — deterministic, dependency-free bag-of-tokens
  embeddings. Used in tests and as an offline/no-API-key fallback so the RAG
  pipeline runs end-to-end with no cloud dependency.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from course_assistant.config import Settings

_TOKEN_RE = re.compile(r"[A-Za-z0-9֐-׿]+")  # Latin + Hebrew


@runtime_checkable
class Embedder(Protocol):
    """Turns text into vectors. Documents and queries embed into the same space."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm else vec


class HashingEmbedder:
    """Deterministic hashed bag-of-tokens embedder (no dependencies, no network).

    Tokens are hashed into a fixed-dimension vector; cosine similarity then
    rewards shared vocabulary. Good enough for tests and offline development,
    and fully reproducible (uses ``hashlib``, not Python's salted ``hash``).
    """

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for token in _TOKEN_RE.findall(text.lower()):
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] & 1 else -1.0
            vec[index] += sign
        return _l2_normalize(vec)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed_one(text)


class OpenAIEmbedder:
    """OpenAI embeddings via a lazily-constructed client (never at import)."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Any = None

    def _ensure_client(self) -> Any:  # pragma: no cover - needs a live API key
        if self._client is None:
            from openai import OpenAI

            if self._settings.openai_api_key is None:
                raise RuntimeError("OPENAI_API_KEY is required for OpenAI embeddings.")
            self._client = OpenAI(api_key=self._settings.openai_api_key.get_secret_value())
        return self._client

    def _embed(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        client = self._ensure_client()
        resp = client.embeddings.create(model=self._settings.embedding_model, input=texts)
        return [item.embedding for item in resp.data]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:  # pragma: no cover
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:  # pragma: no cover
        return self._embed([text])[0]
