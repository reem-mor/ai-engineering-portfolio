"""Tests for the email service layer (recipients, fake sender, selection)."""

from __future__ import annotations

import pytest

from course_assistant.config import Settings
from course_assistant.homework.email import (
    EmailMessage,
    EmailSendError,
    GmailEmailService,
    RecordingEmailService,
    build_email_service,
    recipients_from_settings,
)


def _settings(**kw: object) -> Settings:
    return Settings(_env_file=None, **kw)  # type: ignore[call-arg]


def test_recipients_parse_to_and_multiple_cc() -> None:
    settings = _settings(
        hw_to_email="alex@example.com",
        hw_cc_email="sagy1@example.com, sagy2@example.com",
    )
    to, cc = recipients_from_settings(settings)
    assert to == ["alex@example.com"]
    assert cc == ["sagy1@example.com", "sagy2@example.com"]


def test_missing_to_raises() -> None:
    with pytest.raises(EmailSendError, match="HW_TO_EMAIL"):
        recipients_from_settings(_settings(hw_to_email=None))


def test_recording_service_records_messages() -> None:
    service = RecordingEmailService()
    message = EmailMessage(to=["a@x.com"], cc=[], subject="s", body="b")
    service.send(message)
    assert service.sent == [message]


def test_build_email_service_returns_gmail() -> None:
    assert isinstance(build_email_service(_settings()), GmailEmailService)
