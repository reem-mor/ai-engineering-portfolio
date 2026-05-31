"""Small text helpers for workflow UI."""
from __future__ import annotations

import re


def format_citation_label(source_uri: str | None) -> str:
    """Human-readable document name from any S3 or file URI."""
    if not source_uri:
        return "Unknown source"
    path = source_uri.split("://", 1)[-1]
    name = path.rsplit("/", 1)[-1]
    return name or "Unknown source"


def parse_action_bullets(answer: str, *, limit: int = 8) -> list[str]:
    """Heuristic: pull list-like lines from a free-text model answer."""
    bullets: list[str] = []
    for line in answer.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = re.match(r"^[-*•]\s+(.+)$", stripped)
        if match:
            bullets.append(match.group(1).strip())
            continue
        match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if match:
            bullets.append(match.group(1).strip())
    if bullets:
        return bullets[:limit]
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", answer) if len(s.strip()) > 20]
    return sentences[: min(limit, 4)]
