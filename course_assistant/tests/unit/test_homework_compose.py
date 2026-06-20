"""Byte-level tests for homework email composition."""

from __future__ import annotations

from course_assistant.homework.compose import compose_body, compose_email, compose_subject
from course_assistant.homework.models import Attachment, SubmissionDraft


def _full_draft() -> SubmissionDraft:
    return SubmissionDraft(
        full_name="John Doe",
        topic="Python Basics",
        date="12/05/2026",
        implemented="a CLI calculator with a parser",
        main_focus="recursion and error handling",
        challenges="floating-point rounding",
        challenge_solution="using the decimal module",
        github_link="https://github.com/john/calc",
        attachments=[Attachment("calc.py"), Attachment("report.pdf")],
    )


def test_subject_is_exact_with_en_dash() -> None:
    subject = compose_subject(_full_draft())
    assert subject == "[Oz VeRuach] Homework Submission – John Doe – Python Basics – 12/05/2026"
    assert "–" in subject  # en dash, not a hyphen


def test_body_follows_procedure_structure() -> None:
    body = compose_body(_full_draft(), greeting_name="Alex")
    assert body.startswith("Hello Alex,\n")
    assert "I am submitting my homework for the Python Basics assignment." in body
    assert "In this assignment, I implemented a CLI calculator with a parser." in body
    assert "The main focus was recursion and error handling." in body
    assert (
        "During the process, I encountered floating-point rounding, "
        "and addressed them by using the decimal module." in body
    )
    assert "Please find attached:" in body
    assert "- calc.py" in body
    assert "- report.pdf" in body
    assert "- GitHub: https://github.com/john/calc" in body
    assert body.rstrip().endswith("Best regards,\nJohn Doe")


def test_optional_lines_omitted_when_absent() -> None:
    draft = SubmissionDraft(
        full_name="Dana",
        topic="Docker",
        date="01/06/2026",
        implemented="a Dockerfile",
        attachments=[Attachment("Dockerfile")],
    )
    body = compose_body(draft)
    assert "The main focus was" not in body
    assert "During the process" not in body


def test_compose_email_combines_subject_and_body() -> None:
    email = compose_email(_full_draft(), greeting_name="Alex")
    assert email.subject.startswith("[Oz VeRuach] Homework Submission –")
    assert "Hello Alex," in email.body
