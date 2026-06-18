"""Email service interface.

One interface, two backends (Gmail API primary, SMTP+App-Password fallback). Recipient
addresses come from config (``HW_TO_EMAIL`` / ``HW_CC_EMAIL``), never hardcoded.
Concrete sending and the submission flow land in Phase 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class EmailAttachment:
    """An attachment to include in an outgoing email."""

    filename: str
    content: bytes
    mime_type: str


@runtime_checkable
class EmailService(Protocol):
    """Sends homework submission emails."""

    async def send(
        self,
        *,
        to: str,
        cc: str | None,
        subject: str,
        body: str,
        attachments: list[EmailAttachment],
    ) -> str:
        """Send an email and return the provider message id."""
        ...
