"""Tests for the submission flow: preview → confirm → send."""

from __future__ import annotations

import pytest

from course_assistant.config import Settings
from course_assistant.homework.email import RecordingEmailService
from course_assistant.homework.models import Attachment, SubmissionDraft, SubmissionError
from course_assistant.homework.submission import (
    build_message,
    render_preview,
    send_submission,
)


def _settings() -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        hw_to_email="alex@example.com",
        hw_cc_email="sagy1@example.com, sagy2@example.com",
        hw_to_name="Alex",
    )


def _draft() -> SubmissionDraft:
    return SubmissionDraft(
        full_name="Dana Levi",
        topic="Docker & AWS",
        date="01/06/2026",
        implemented="an EC2 deployment with nginx",
        attachments=[Attachment("notes.md")],
        github_link="https://github.com/dana/deploy",
    )


def test_build_message_uses_settings_recipients() -> None:
    msg = build_message(_draft(), _settings())
    assert msg.to == ["alex@example.com"]
    assert msg.cc == ["sagy1@example.com", "sagy2@example.com"]
    assert msg.subject == "[Oz VeRuach] Homework Submission – Dana Levi – Docker & AWS – 01/06/2026"
    assert "Hello Alex," in msg.body


def test_render_preview_moves_to_preview_and_shows_fields() -> None:
    draft = _draft()
    preview = render_preview(draft, _settings(), lang="en")
    assert draft.state.name == "PREVIEW"
    assert "To: alex@example.com" in preview
    assert "Cc: sagy1@example.com, sagy2@example.com" in preview
    assert "Subject: [Oz VeRuach] Homework Submission –" in preview
    assert "notes.md" in preview
    assert "confirm" in preview.lower()


def test_send_requires_confirmation() -> None:
    draft = _draft()
    service = RecordingEmailService()
    render_preview(draft, _settings())  # PREVIEW, not yet confirmed
    with pytest.raises(SubmissionError, match="confirmed"):
        send_submission(draft, service, _settings())
    assert service.sent == []


def test_full_flow_sends_once_and_blocks_double_send() -> None:
    draft = _draft()
    service = RecordingEmailService()
    render_preview(draft, _settings())
    draft.confirm()
    message = send_submission(draft, service, _settings())

    assert len(service.sent) == 1
    assert service.sent[0] is message
    assert message.to == ["alex@example.com"]
    # Draft is now SENT — a second send must not deliver again.
    with pytest.raises(SubmissionError):
        send_submission(draft, service, _settings())
    assert len(service.sent) == 1
