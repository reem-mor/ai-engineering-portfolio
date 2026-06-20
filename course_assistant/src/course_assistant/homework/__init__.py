"""Homework submission: explain the procedure, compose, preview, and send."""

from course_assistant.homework.compose import ComposedEmail, compose_email
from course_assistant.homework.email import (
    EmailMessage,
    EmailSendError,
    EmailService,
    GmailEmailService,
    RecordingEmailService,
    build_email_service,
)
from course_assistant.homework.guardrail import homework_help_disclaimer, looks_like_solve_request
from course_assistant.homework.models import (
    Attachment,
    SubmissionDraft,
    SubmissionError,
    SubmissionState,
)
from course_assistant.homework.submission import build_message, render_preview, send_submission

__all__ = [
    "Attachment",
    "ComposedEmail",
    "EmailMessage",
    "EmailSendError",
    "EmailService",
    "GmailEmailService",
    "RecordingEmailService",
    "SubmissionDraft",
    "SubmissionError",
    "SubmissionState",
    "build_email_service",
    "build_message",
    "compose_email",
    "homework_help_disclaimer",
    "looks_like_solve_request",
    "render_preview",
    "send_submission",
]
