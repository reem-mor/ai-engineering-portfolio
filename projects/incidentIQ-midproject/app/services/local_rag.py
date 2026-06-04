"""Pure-Python TF-IDF + keyword retriever for offline RAG.

This module powers the local demo mode so the application never depends on a
network call to Amazon Bedrock. It loads markdown runbooks from
``knowledge_base/runbooks/`` (falling back to ``data/sample_documents/``),
splits them into heading-delimited chunks, and ranks chunks against a query
with a small TF-IDF cosine similarity implemented without third-party
dependencies. Every hit carries the source document name and an excerpt so the
agent can cite it.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.validators import tokenize

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PRIMARY_DIR = _PROJECT_ROOT / "knowledge_base" / "runbooks"
_FALLBACK_DIR = _PROJECT_ROOT / "data" / "sample_documents"

# Minimum cosine score for a chunk to count as a grounded retrieval. Below this
# the retriever reports no match so the agent can refuse instead of guessing.
# Tuned so on-topic incident queries (~0.45+) ground cleanly while off-topic
# noise (incidental shared tokens, ~0.20) stays below the bar and triggers refusal.
MIN_SCORE = 0.22


@dataclass(frozen=True)
class RetrievedChunk:
    """A single ranked chunk of a runbook."""

    document: str
    excerpt: str
    score: float
    chunk_index: int


def _split_chunks(text: str) -> list[str]:
    """Split a markdown document into heading-delimited chunks."""
    lines = text.splitlines()
    chunks: list[str] = []
    buffer: list[str] = []
    for line in lines:
        if line.startswith("#") and buffer:
            chunk = "\n".join(buffer).strip()
            if chunk:
                chunks.append(chunk)
            buffer = [line]
        else:
            buffer.append(line)
    tail = "\n".join(buffer).strip()
    if tail:
        chunks.append(tail)
    # Fall back to the whole document if there were no headings.
    if not chunks and text.strip():
        chunks.append(text.strip())
    return chunks


class LocalRetriever:
    """TF-IDF retriever over a directory of markdown/text runbooks."""

    def __init__(self, *, runbook_dir: Path | None = None) -> None:
        self._dir = runbook_dir or (
            _PRIMARY_DIR if _PRIMARY_DIR.is_dir() else _FALLBACK_DIR
        )
        self._documents: list[RetrievedChunk] = []
        self._chunk_tokens: list[list[str]] = []
        self._idf: dict[str, float] = {}
        self._chunk_vectors: list[dict[str, float]] = []
        self._load()

    @property
    def runbook_dir(self) -> Path:
        return self._dir

    def document_count(self) -> int:
        return len({c.document for c in self._documents})

    def _load(self) -> None:
        if not self._dir.is_dir():
            return
        raw_chunks: list[tuple[str, int, str]] = []
        for path in sorted(self._dir.glob("*.md")) + sorted(self._dir.glob("*.txt")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for idx, chunk in enumerate(_split_chunks(text)):
                raw_chunks.append((path.name, idx, chunk))

        self._chunk_tokens = [tokenize(chunk) for _, _, chunk in raw_chunks]
        self._documents = [
            RetrievedChunk(document=name, excerpt=chunk, score=0.0, chunk_index=idx)
            for name, idx, chunk in raw_chunks
        ]

        n_docs = len(self._chunk_tokens) or 1
        df: dict[str, int] = {}
        for tokens in self._chunk_tokens:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1
        self._idf = {
            term: math.log((n_docs + 1) / (freq + 1)) + 1.0
            for term, freq in df.items()
        }
        self._chunk_vectors = [self._vectorize(tokens) for tokens in self._chunk_tokens]

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        counts: dict[str, int] = {}
        for term in tokens:
            counts[term] = counts.get(term, 0) + 1
        vector = {
            term: (count / len(tokens)) * self._idf.get(term, 1.0)
            for term, count in counts.items()
        }
        norm = math.sqrt(sum(weight * weight for weight in vector.values()))
        if norm == 0:
            return {}
        return {term: weight / norm for term, weight in vector.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        smaller, larger = (a, b) if len(a) <= len(b) else (b, a)
        return sum(weight * larger.get(term, 0.0) for term, weight in smaller.items())

    def search(self, query: str, *, top_k: int = 4) -> list[RetrievedChunk]:
        """Return the top-k chunks ranked by TF-IDF cosine similarity."""
        query_vector = self._vectorize(tokenize(query))
        if not query_vector or not self._chunk_vectors:
            return []
        scored: list[RetrievedChunk] = []
        for chunk, vector in zip(self._documents, self._chunk_vectors):
            score = self._cosine(query_vector, vector)
            if score >= MIN_SCORE:
                scored.append(
                    RetrievedChunk(
                        document=chunk.document,
                        excerpt=chunk.excerpt,
                        score=round(score, 4),
                        chunk_index=chunk.chunk_index,
                    )
                )
        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[: max(1, top_k)]


@lru_cache(maxsize=4)
def get_retriever(runbook_dir: str | None = None) -> LocalRetriever:
    """Cached retriever so the corpus is parsed once per process."""
    return LocalRetriever(runbook_dir=Path(runbook_dir) if runbook_dir else None)


def _first_excerpt_steps(excerpt: str) -> list[str]:
    """Pull numbered or bulleted action lines out of a runbook chunk."""
    steps: list[str] = []
    for line in excerpt.splitlines():
        stripped = line.strip()
        match = re.match(r"^(?:\d+[.)]|[-*])\s+(.*)", stripped)
        if match:
            text = match.group(1).strip()
            if text:
                steps.append(text)
    return steps
