"""In-memory session store for incident triage and follow-up turns.

One session per incident keyed by ``session_id``. Stores the alert, RAG
citations, tool outputs, the final triage card, and a follow-up history so
follow-up questions reuse prior results instead of re-running the tools.

This is intentionally a process-local dict (thread-safe with a lock). It is the
right scope for a single-instance demo; a multi-instance deployment would swap
this for Redis or a database behind the same small interface.
"""
from __future__ import annotations

import threading
import time
import uuid
from typing import Any

_LOCK = threading.Lock()
_SESSIONS: dict[str, dict[str, Any]] = {}

# Cap retained sessions so a long-running demo cannot grow unbounded.
_MAX_SESSIONS = 200


def create_session(alert: dict[str, Any], *, session_id: str | None = None) -> str:
    """Create (or reset) a session for an alert and return its id."""
    sid = (session_id or "").strip() or str(uuid.uuid4())
    with _LOCK:
        if len(_SESSIONS) >= _MAX_SESSIONS:
            oldest = min(_SESSIONS, key=lambda k: _SESSIONS[k]["created_at"])
            _SESSIONS.pop(oldest, None)
        _SESSIONS[sid] = {
            "session_id": sid,
            "created_at": time.time(),
            "alert": dict(alert),
            "citations": [],
            "tool_outputs": {},
            "triage_card": None,
            "followups": [],
        }
    return sid


def save_triage(
    session_id: str,
    *,
    citations: list[dict[str, Any]],
    tool_outputs: dict[str, Any],
    triage_card: dict[str, Any],
) -> None:
    """Persist the triage result (citations, tool outputs, final card)."""
    with _LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            return
        session["citations"] = citations
        session["tool_outputs"] = tool_outputs
        session["triage_card"] = triage_card


def get_session(session_id: str | None) -> dict[str, Any] | None:
    """Return a shallow copy of the session, or ``None`` if unknown."""
    if not session_id:
        return None
    with _LOCK:
        session = _SESSIONS.get(session_id)
        return dict(session) if session is not None else None


def append_followup(session_id: str, question: str, answer: dict[str, Any]) -> bool:
    """Record a follow-up Q/A turn. Returns False if the session is unknown."""
    with _LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            return False
        session["followups"].append({"question": question, "answer": answer, "ts": time.time()})
        return True


def reset() -> None:
    """Clear all sessions (tests/demo reset)."""
    with _LOCK:
        _SESSIONS.clear()
