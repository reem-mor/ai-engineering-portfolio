"""Vector-store interface (Phase 1 seam).

Defines the abstraction that RAG retrieval depends on. Concrete backends —
local Chroma (default) and Pinecone (swappable upgrade) — are implemented in
Phase 3 behind this interface, so the agent and ingestion code never import a
backend directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class Document:
    """A chunk of course material to embed and store."""

    id: str
    text: str
    source: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    """A retrieval hit: the matched chunk plus its similarity score."""

    document: Document
    score: float


@runtime_checkable
class VectorStore(Protocol):
    """Minimal contract every vector-store backend must satisfy."""

    def add(self, documents: list[Document]) -> None:
        """Embed and upsert ``documents`` into the store."""
        ...

    def search(self, query: str, k: int = 4) -> list[SearchResult]:
        """Return the top-``k`` most similar chunks to ``query`` with sources."""
        ...

    def clear(self) -> None:
        """Remove all stored documents (used for a clean re-ingest)."""
        ...
