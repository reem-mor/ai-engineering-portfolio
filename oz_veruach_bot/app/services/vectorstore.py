"""Vector store interface.

Primary: Supabase Postgres + pgvector; dev fallback: SQLite + a local vector lib. Both
behind this interface. Embeddings via ``text-embedding-3-small``. Concrete stores and
indexing land in Phase 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A retrieved material chunk with its similarity score and source link."""

    text: str
    score: float
    drive_file_id: str
    view_url: str


@runtime_checkable
class VectorStore(Protocol):
    """Stores and retrieves embedded course-material chunks."""

    async def upsert(
        self, *, chunk_id: str, text: str, embedding: list[float], metadata: dict[str, str]
    ) -> None:
        """Insert or update a chunk and its embedding."""
        ...

    async def query(self, *, embedding: list[float], top_k: int) -> list[RetrievedChunk]:
        """Return the top-k most similar chunks for a query embedding."""
        ...
