"""Deterministic homework-email composition.

Produces the subject and body byte-for-byte per the course's
``Homework_Submission_Procedure`` document. The subject uses an en dash (–,
U+2013) exactly as the procedure specifies; the body is always English (the
procedure requires it), regardless of the chat language.
"""

from __future__ import annotations

from dataclasses import dataclass

from course_assistant.homework.models import SubmissionDraft

EN_DASH = "–"
SUBJECT_PREFIX = "[Oz VeRuach] Homework Submission"
DEFAULT_GREETING_NAME = "Alex"


@dataclass(frozen=True)
class ComposedEmail:
    """A rendered subject + body ready to preview or send."""

    subject: str
    body: str


def compose_subject(draft: SubmissionDraft) -> str:
    """``[Oz VeRuach] Homework Submission – <Name> – <Topic> – <Date>``."""
    parts = [SUBJECT_PREFIX, draft.full_name or "", draft.topic or "", draft.date or ""]
    return f" {EN_DASH} ".join(parts)


def _attachment_bullets(draft: SubmissionDraft) -> list[str]:
    bullets = [f"- {a.filename}" for a in draft.attachments]
    if draft.github_link:
        bullets.append(f"- GitHub: {draft.github_link}")
    return bullets


def compose_body(draft: SubmissionDraft, greeting_name: str = DEFAULT_GREETING_NAME) -> str:
    """Render the professional English body following the procedure's structure."""
    lines: list[str] = [f"Hello {greeting_name},", ""]
    lines.append(f"I am submitting my homework for the {draft.topic} assignment.")
    lines.append(f"In this assignment, I implemented {draft.implemented}.")
    if draft.main_focus:
        lines.append(f"The main focus was {draft.main_focus}.")
    if draft.challenges:
        sentence = f"During the process, I encountered {draft.challenges}"
        if draft.challenge_solution:
            sentence += f", and addressed them by {draft.challenge_solution}"
        lines.append(sentence + ".")

    lines.append("")
    lines.append("Please find attached:")
    lines.extend(_attachment_bullets(draft))
    lines.append("")
    lines.append("I would appreciate your feedback.")
    lines.append("")
    lines.append("Best regards,")
    lines.append(draft.full_name or "")
    return "\n".join(lines)


def compose_email(
    draft: SubmissionDraft, greeting_name: str = DEFAULT_GREETING_NAME
) -> ComposedEmail:
    """Compose the full email (subject + body) for a draft."""
    return ComposedEmail(
        subject=compose_subject(draft),
        body=compose_body(draft, greeting_name),
    )
