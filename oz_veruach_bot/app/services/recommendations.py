"""Recommendations interface.

Combines curated ``resources.yaml`` topic->links, RAG over indexed course materials, and
an optional web-search tool. Concrete logic lands in Phase 6.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Recommendation:
    """A single recommended resource with a title and link."""

    title: str
    url: str
    source: str  # "course" | "external"


@runtime_checkable
class RecommendationService(Protocol):
    """Recommends learning materials for a topic or lesson."""

    async def recommend(
        self, *, topic: str, allow_web: bool, language: str
    ) -> list[Recommendation]:
        """Return a short, ranked list of recommended resources."""
        ...
