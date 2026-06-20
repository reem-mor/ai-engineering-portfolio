"""Orchestrates the homework submission flow: preview → confirm → send.

Ties the draft, composition, and email service together. Sending is guarded:
the draft must be in the ``CONFIRMED`` state (i.e. the student approved the
preview) before an email leaves.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from course_assistant.homework.compose import compose_email
from course_assistant.homework.email import (
    EmailMessage,
    EmailService,
    recipients_from_settings,
)
from course_assistant.homework.models import SubmissionDraft, SubmissionError, SubmissionState

if TYPE_CHECKING:
    from course_assistant.config import Settings

_PREVIEW = {
    "he": {
        "to": "אל",
        "cc": "עותק",
        "subject": "נושא",
        "attachments": "קבצים מצורפים",
        "none": "(אין)",
        "confirm_hint": "לאישור ושליחה השב 'אשר'; לביטול השב 'בטל'.",
    },
    "en": {
        "to": "To",
        "cc": "Cc",
        "subject": "Subject",
        "attachments": "Attachments",
        "none": "(none)",
        "confirm_hint": "Reply 'confirm' to send, or 'cancel' to discard.",
    },
}


def _lang(lang: str) -> str:
    return "he" if lang.lower().startswith("he") else "en"


def build_message(draft: SubmissionDraft, settings: Settings) -> EmailMessage:
    """Build the :class:`EmailMessage` for a ready draft (recipients from settings)."""
    to, cc = recipients_from_settings(settings)
    greeting = to[0].split("@")[0].split(".")[0].capitalize() if to else "Alex"
    if settings.hw_to_name:
        greeting = settings.hw_to_name
    email = compose_email(draft, greeting_name=greeting)
    return EmailMessage(
        to=to,
        cc=cc,
        subject=email.subject,
        body=email.body,
        attachments=list(draft.attachments),
    )


def render_preview(draft: SubmissionDraft, settings: Settings, lang: str = "he") -> str:
    """Render a human-readable preview and move the draft into ``PREVIEW`` state."""
    draft.to_preview()
    message = build_message(draft, settings)
    t = _PREVIEW[_lang(lang)]
    attachments = (
        "\n".join(f"  - {a.filename}" for a in message.attachments) or f"  {t['none']}"
    )
    return "\n".join(
        [
            f"{t['to']}: {', '.join(message.to)}",
            f"{t['cc']}: {', '.join(message.cc) or t['none']}",
            f"{t['subject']}: {message.subject}",
            "",
            message.body,
            "",
            f"{t['attachments']}:",
            attachments,
            "",
            t["confirm_hint"],
        ]
    )


def send_submission(
    draft: SubmissionDraft, service: EmailService, settings: Settings
) -> EmailMessage:
    """Send a confirmed submission. Raises if the draft hasn't been confirmed."""
    if draft.state is not SubmissionState.CONFIRMED:
        raise SubmissionError("Draft must be confirmed before sending.")
    message = build_message(draft, settings)
    service.send(message)
    draft.mark_sent()
    return message
