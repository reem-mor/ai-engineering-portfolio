"""Notifier interface.

Broadcasts to subscribers with throttling (Telegram ~30 msg/s global + per-chat limits)
and idempotency (never notify twice for the same event). Concrete sender + token-bucket
land in Phase 5.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class BroadcastResult:
    """Outcome of a broadcast: how many chats succeeded vs failed."""

    sent: int
    failed: int


@runtime_checkable
class Notifier(Protocol):
    """Sends throttled, idempotent broadcasts to subscribers."""

    async def broadcast(self, *, idempotency_key: str, message: str) -> BroadcastResult:
        """Broadcast a message to all subscribers exactly once per key."""
        ...
