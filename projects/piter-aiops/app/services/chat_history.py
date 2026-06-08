"""Process-local chat message history for the demo API contract."""
from __future__ import annotations

import threading
import time
from typing import Any

DEFAULT_SESSION_ID = "demo-default"

_LOCK = threading.Lock()
_MESSAGES: dict[str, list[dict[str, Any]]] = {DEFAULT_SESSION_ID: []}


def _session_id(session_id: str | None) -> str:
    sid = (session_id or "").strip()
    return sid or DEFAULT_SESSION_ID


def append_turn(
    *,
    session_id: str | None,
    question: str,
    answer: str,
    mode: str | None = None,
) -> None:
    """Record one user/assistant exchange."""
    sid = _session_id(session_id)
    now = time.time()
    with _LOCK:
        bucket = _MESSAGES.setdefault(sid, [])
        bucket.append(
            {
                "role": "user",
                "content": question,
                "ts": now,
            }
        )
        bucket.append(
            {
                "role": "assistant",
                "content": answer,
                "ts": now,
                "mode": mode,
            }
        )


def get_messages(session_id: str | None = None) -> dict[str, Any]:
    """Return chat messages for a session (empty list if none yet)."""
    sid = _session_id(session_id)
    with _LOCK:
        messages = list(_MESSAGES.get(sid, []))
    return {
        "session_id": sid,
        "messages": messages,
        "count": len(messages),
    }


def clear_history(session_id: str | None = None) -> dict[str, Any]:
    """Clear chat history for one session or all sessions."""
    sid = (session_id or "").strip()
    with _LOCK:
        if sid:
            removed = len(_MESSAGES.get(sid, []))
            _MESSAGES[sid] = []
            return {"session_id": sid, "cleared": removed}
        total = sum(len(v) for v in _MESSAGES.values())
        _MESSAGES.clear()
        _MESSAGES[DEFAULT_SESSION_ID] = []
        return {"session_id": None, "cleared": total}


def reset() -> None:
    """Clear all history (tests)."""
    with _LOCK:
        _MESSAGES.clear()
        _MESSAGES[DEFAULT_SESSION_ID] = []
