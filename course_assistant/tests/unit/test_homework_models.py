"""Tests for the SubmissionDraft state machine."""

from __future__ import annotations

import pytest

from course_assistant.homework.models import (
    Attachment,
    SubmissionDraft,
    SubmissionError,
    SubmissionState,
)


def _ready_draft() -> SubmissionDraft:
    return SubmissionDraft(
        full_name="Dana",
        topic="Docker",
        date="01/06/2026",
        implemented="a Dockerfile",
        attachments=[Attachment("Dockerfile")],
    )


def test_missing_fields_lists_required_only() -> None:
    draft = SubmissionDraft(full_name="Dana")
    assert set(draft.missing_fields()) == {"topic", "implemented", "date"}


def test_requires_a_deliverable() -> None:
    draft = SubmissionDraft(
        full_name="Dana", topic="Docker", date="01/06/2026", implemented="x"
    )
    assert draft.missing_fields() == []
    assert not draft.has_deliverable()
    assert not draft.is_ready()
    with pytest.raises(SubmissionError, match="at least one file or a GitHub link"):
        draft.to_preview()


def test_github_link_counts_as_deliverable() -> None:
    draft = SubmissionDraft(
        full_name="Dana",
        topic="Docker",
        date="01/06/2026",
        implemented="x",
        github_link="https://github.com/dana/x",
    )
    assert draft.is_ready()


def test_happy_path_transitions() -> None:
    draft = _ready_draft()
    draft.to_preview()
    assert draft.state is SubmissionState.PREVIEW
    draft.confirm()
    assert draft.state is SubmissionState.CONFIRMED
    draft.mark_sent()
    assert draft.state is SubmissionState.SENT


def test_cannot_confirm_before_preview() -> None:
    with pytest.raises(SubmissionError):
        _ready_draft().confirm()


def test_cannot_send_before_confirm() -> None:
    draft = _ready_draft()
    draft.to_preview()
    with pytest.raises(SubmissionError):
        draft.mark_sent()


def test_cannot_cancel_after_sent() -> None:
    draft = _ready_draft()
    draft.to_preview()
    draft.confirm()
    draft.mark_sent()
    with pytest.raises(SubmissionError):
        draft.cancel()
