"""Text chunking for RAG ingestion.

Pure, dependency-free, and deterministic so chunk boundaries are easy to test.
Whitespace is collapsed, then a sliding character window snaps to word
boundaries with a configurable overlap between consecutive chunks.
"""

from __future__ import annotations

DEFAULT_CHUNK_SIZE = 800
DEFAULT_OVERLAP = 150


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[str]:
    """Split ``text`` into overlapping, word-aligned chunks.

    Args:
        text: Source text (whitespace is collapsed first).
        chunk_size: Target maximum characters per chunk.
        overlap: Characters of trailing context repeated at the next chunk's start.

    Returns:
        A list of non-empty chunks. Empty/whitespace input yields ``[]``;
        text shorter than ``chunk_size`` yields a single chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    normalized = " ".join(text.split())
    if not normalized:
        return []
    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    n = len(normalized)
    while start < n:
        end = start + chunk_size
        if end >= n:
            chunks.append(normalized[start:].strip())
            break
        # Snap the cut back to the last space so we don't split a word.
        space = normalized.rfind(" ", start, end)
        cut = space if space > start else end
        chunks.append(normalized[start:cut].strip())
        # Step forward with overlap, guaranteeing forward progress.
        next_start = cut - overlap
        start = next_start if next_start > start else cut
    return [c for c in chunks if c]
