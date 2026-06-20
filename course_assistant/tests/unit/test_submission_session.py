"""Tests for the guided homework SubmissionSession."""

from __future__ import annotations

from course_assistant.config import Settings
from course_assistant.homework.email import RecordingEmailService
from course_assistant.homework.session import SubmissionSession


def _settings() -> Settings:
    return Settings(  # type: ignore[call-arg]
        _env_file=None,
        hw_to_email="alex@example.com",
        hw_cc_email="sagy@example.com",
        hw_to_name="Alex",
    )


def _session(service: RecordingEmailService, lang: str = "en") -> SubmissionSession:
    return SubmissionSession(
        settings=_settings(),
        email_service=service,
        lang=lang,
        today=lambda: "01/06/2026",
    )


def test_full_flow_collects_previews_and_sends() -> None:
    service = RecordingEmailService()
    session = _session(service)

    session.start()
    session.handle("Dana Levi")  # full_name
    session.handle("Docker & AWS")  # topic
    session.handle("an EC2 deployment")  # implemented
    session.handle("-")  # main_focus skipped
    session.handle("-")  # challenges skipped
    preview = session.handle("https://github.com/dana/deploy")  # github_link → preview

    assert "Email preview:" in preview
    assert "alex@example.com" in preview
    assert "[Oz VeRuach] Homework Submission – Dana Levi – Docker & AWS – 01/06/2026" in preview
    assert not session.done

    result = session.handle("confirm")
    assert "sent" in result.lower()
    assert session.done
    assert len(service.sent) == 1
    sent = service.sent[0]
    assert sent.to == ["alex@example.com"]
    assert sent.cc == ["sagy@example.com"]
    assert "Hello Alex," in sent.body


def test_cancel_does_not_send() -> None:
    service = RecordingEmailService()
    session = _session(service)
    session.start()
    session.handle("Dana")
    session.handle("Docker")
    session.handle("a Dockerfile")
    session.handle("-")
    session.handle("-")
    session.handle("https://github.com/dana/x")  # → preview
    out = session.handle("cancel")

    assert "cancelled" in out.lower()
    assert session.done
    assert service.sent == []


def test_required_field_reasked_on_skip() -> None:
    service = RecordingEmailService()
    session = _session(service)
    first = session.start()  # asks full_name (required)
    again = session.handle("-")  # skip not allowed for required
    assert again == first


def test_confirmation_prompt_on_unrecognized_reply() -> None:
    service = RecordingEmailService()
    session = _session(service)
    session.start()
    session.handle("Dana")
    session.handle("Docker")
    session.handle("a Dockerfile")
    session.handle("-")
    session.handle("-")
    session.handle("https://github.com/dana/x")  # → preview
    out = session.handle("maybe later")  # neither confirm nor cancel
    assert "confirm" in out.lower()
    assert not session.done
    assert service.sent == []
