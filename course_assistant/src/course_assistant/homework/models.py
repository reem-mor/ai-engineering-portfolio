"""Homework submission draft + state machine.

A :class:`SubmissionDraft` collects the fields a student provides, validates them,
and moves through ``drafting → preview → confirmed → sent`` (or ``cancelled``).
Sending is only possible once the student has explicitly confirmed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto


class SubmissionState(StrEnum):
    """Lifecycle of a homework submission."""

    DRAFTING = auto()
    PREVIEW = auto()
    CONFIRMED = auto()
    SENT = auto()
    CANCELLED = auto()


@dataclass(frozen=True)
class Attachment:
    """A file to attach. ``content`` is ``None`` until the bytes are supplied."""

    filename: str
    content: bytes | None = None


class SubmissionError(RuntimeError):
    """Raised on an invalid state transition or send precondition."""


# Fields required before a draft can be previewed/sent.
_REQUIRED_FIELDS = ("full_name", "topic", "implemented", "date")


@dataclass
class SubmissionDraft:
    """A mutable homework-submission draft with an explicit state machine."""

    full_name: str | None = None
    topic: str | None = None
    date: str | None = None  # e.g. "12/05/2026"
    implemented: str | None = None
    main_focus: str | None = None
    challenges: str | None = None
    challenge_solution: str | None = None
    github_link: str | None = None
    attachments: list[Attachment] = field(default_factory=list)
    state: SubmissionState = SubmissionState.DRAFTING

    # -- validation ---------------------------------------------------------

    def missing_fields(self) -> list[str]:
        """Required fields that are still empty."""
        return [name for name in _REQUIRED_FIELDS if not getattr(self, name)]

    def has_deliverable(self) -> bool:
        """True if there is something to hand in (a file or a GitHub link)."""
        return bool(self.attachments) or bool(self.github_link)

    def is_ready(self) -> bool:
        """True if the draft can be previewed/sent."""
        return not self.missing_fields() and self.has_deliverable()

    # -- transitions --------------------------------------------------------

    def to_preview(self) -> None:
        if self.missing_fields():
            raise SubmissionError(f"Missing required fields: {', '.join(self.missing_fields())}")
        if not self.has_deliverable():
            raise SubmissionError("Attach at least one file or a GitHub link before previewing.")
        self.state = SubmissionState.PREVIEW

    def confirm(self) -> None:
        if self.state is not SubmissionState.PREVIEW:
            raise SubmissionError("Can only confirm a draft that is in preview.")
        self.state = SubmissionState.CONFIRMED

    def mark_sent(self) -> None:
        if self.state is not SubmissionState.CONFIRMED:
            raise SubmissionError("Can only send a draft that has been confirmed.")
        self.state = SubmissionState.SENT

    def cancel(self) -> None:
        if self.state in (SubmissionState.SENT, SubmissionState.CANCELLED):
            raise SubmissionError(f"Cannot cancel a draft in state {self.state}.")
        self.state = SubmissionState.CANCELLED
