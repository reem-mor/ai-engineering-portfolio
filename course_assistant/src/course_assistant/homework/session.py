"""A guided, framework-agnostic homework-submission conversation.

Drives the Phase 4 submission flow one question at a time, shows a preview, and
sends only after the student types a confirmation word. Interface-agnostic so the
Telegram adapter (or a test) can feed it text and render its replies.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date as date_cls
from enum import Enum, auto

from course_assistant.config import Settings
from course_assistant.homework.email import EmailService
from course_assistant.homework.models import Attachment, SubmissionDraft
from course_assistant.homework.submission import render_preview, send_submission


def _default_today() -> str:
    return date_cls.today().strftime("%d/%m/%Y")


_CONFIRM_WORDS = {"confirm", "yes", "send", "אשר", "אישור", "שלח", "כן"}
_CANCEL_WORDS = {"cancel", "no", "stop", "בטל", "ביטול", "לא", "עצור"}
_SKIP_WORDS = {"-", "skip", "דלג", "אין"}


class _Phase(Enum):
    COLLECTING = auto()
    AWAITING_CONFIRM = auto()
    DONE = auto()


@dataclass(frozen=True)
class _Step:
    field: str
    required: bool
    prompt_he: str
    prompt_en: str

    def prompt(self, lang: str) -> str:
        return self.prompt_he if lang.lower().startswith("he") else self.prompt_en


_STEPS: list[_Step] = [
    _Step("full_name", True, "מה שמך המלא?", "What's your full name?"),
    _Step("topic", True, "מה הנושא/המטלה?", "What's the topic/assignment?"),
    _Step("implemented", True, "מה מימשת או פתרת?", "What did you implement or solve?"),
    _Step(
        "main_focus", False,
        "על מה היה הדגש העיקרי? ('-' לדילוג)",
        "What was the main focus? ('-' to skip)",
    ),
    _Step(
        "challenges", False,
        "אילו אתגרים נתקלת בהם וכיצד פתרת? ('-' לדילוג)",
        "Any challenges and how you addressed them? ('-' to skip)",
    ),
    _Step("github_link", True, "מה קישור ה-GitHub?", "What's your GitHub link?"),
]

_MSG = {
    "he": {
        "cancelled": "ההגשה בוטלה.",
        "sent": "המייל נשלח! בהצלחה 🎓",
        "send_failed": "שליחת המייל נכשלה: {error}",
        "please_confirm": "השב/י 'אשר' לשליחה או 'בטל' לביטול.",
        "preview_header": "תצוגה מקדימה של המייל:",
    },
    "en": {
        "cancelled": "Submission cancelled.",
        "sent": "Email sent! Good luck 🎓",
        "send_failed": "Failed to send the email: {error}",
        "please_confirm": "Reply 'confirm' to send or 'cancel' to abort.",
        "preview_header": "Email preview:",
    },
}


@dataclass
class SubmissionSession:
    """A multi-turn submission conversation backed by a :class:`SubmissionDraft`."""

    settings: Settings
    email_service: EmailService
    lang: str = "he"
    today: Callable[[], str] = _default_today
    draft: SubmissionDraft = field(default_factory=SubmissionDraft)
    _phase: _Phase = _Phase.COLLECTING
    _step_index: int = 0

    @property
    def done(self) -> bool:
        return self._phase is _Phase.DONE

    def add_attachment(self, attachment: Attachment) -> None:
        """Attach a file supplied out-of-band (e.g. a Telegram upload)."""
        self.draft.attachments.append(attachment)

    def start(self) -> str:
        """Return the first prompt."""
        return self._current_step().prompt(self.lang)

    def handle(self, text: str) -> str:
        """Advance the conversation with the user's ``text`` and return the reply."""
        if self._phase is _Phase.AWAITING_CONFIRM:
            return self._handle_confirm(text)
        return self._handle_collect(text)

    # -- internals ----------------------------------------------------------

    def _current_step(self) -> _Step:
        return _STEPS[self._step_index]

    def _handle_collect(self, text: str) -> str:
        step = self._current_step()
        value = text.strip()
        is_skip = value.lower() in _SKIP_WORDS
        if not is_skip:
            setattr(self.draft, step.field, value)
        elif step.required:
            return step.prompt(self.lang)  # re-ask required fields on skip

        self._step_index += 1
        if self._step_index < len(_STEPS):
            return self._current_step().prompt(self.lang)
        return self._enter_preview()

    def _enter_preview(self) -> str:
        if not self.draft.date:
            self.draft.date = self.today()
        preview = render_preview(self.draft, self.settings, lang=self.lang)
        self._phase = _Phase.AWAITING_CONFIRM
        return f"{_MSG[self.lang]['preview_header']}\n\n{preview}"

    def _handle_confirm(self, text: str) -> str:
        word = text.strip().lower()
        if word in _CANCEL_WORDS:
            self.draft.cancel()
            self._phase = _Phase.DONE
            return _MSG[self.lang]["cancelled"]
        if word in _CONFIRM_WORDS:
            self.draft.confirm()
            try:
                send_submission(self.draft, self.email_service, self.settings)
            except Exception as exc:  # noqa: BLE001 - report failure to the user
                self._phase = _Phase.DONE
                return _MSG[self.lang]["send_failed"].format(error=exc)
            self._phase = _Phase.DONE
            return _MSG[self.lang]["sent"]
        return _MSG[self.lang]["please_confirm"]
