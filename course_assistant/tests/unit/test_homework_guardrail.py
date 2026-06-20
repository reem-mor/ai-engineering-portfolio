"""Tests for the anti-'do-my-homework' guardrail and the explain tool."""

from __future__ import annotations

import pytest

from course_assistant.homework.guardrail import (
    homework_help_disclaimer,
    looks_like_solve_request,
)
from course_assistant.tools.homework import explain_homework_submission


@pytest.mark.parametrize(
    "text",
    [
        "can you do my homework for me",
        "Please solve this assignment for me",
        "just write the code for me",
        "give me the answer",
        "תפתור לי את התרגיל",
        "תכתוב לי את הקוד",
    ],
)
def test_solve_requests_are_flagged(text: str) -> None:
    assert looks_like_solve_request(text)


@pytest.mark.parametrize(
    "text",
    [
        "how do I submit my homework?",
        "can you explain recursion?",
        "where are the slides for lesson 3?",
        "help me understand docker",
    ],
)
def test_legitimate_requests_not_flagged(text: str) -> None:
    assert not looks_like_solve_request(text)


def test_disclaimer_is_bilingual() -> None:
    assert "can't complete your homework" in homework_help_disclaimer("en")
    assert "לא יכול לעשות את שיעורי הבית" in homework_help_disclaimer("he")


def test_explain_tool_includes_recipients_and_subject_format() -> None:
    out = explain_homework_submission(lang="en", to_email="alex@x.com", cc_email="sagy@x.com")
    assert "alex@x.com" in out
    assert "sagy@x.com" in out
    assert "[Oz VeRuach] Homework Submission – <Your Full Name> –" in out


def test_explain_tool_hebrew() -> None:
    out = explain_homework_submission(lang="he")
    assert "הגשת שיעורי בית" in out
    assert "Alex" in out  # default recipient names
