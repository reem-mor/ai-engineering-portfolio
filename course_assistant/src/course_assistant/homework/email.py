"""Email delivery behind a small interface.

- :class:`EmailService` — the contract (``send``).
- :class:`GmailEmailService` — production sender via the Gmail API (lazy client;
  scope ``gmail.send``). Never invoked in tests.
- :class:`RecordingEmailService` — an in-memory fake that records sent messages,
  used in tests and local dry-runs.

Recipients are never hardcoded — they come from settings (To: Alex, CC: Sagy).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from course_assistant.homework.models import Attachment

if TYPE_CHECKING:
    from course_assistant.config import Settings


@dataclass(frozen=True)
class EmailMessage:
    """A ready-to-send email."""

    to: list[str]
    cc: list[str]
    subject: str
    body: str
    attachments: list[Attachment] = field(default_factory=list)


class EmailSendError(RuntimeError):
    """Raised when delivery fails or the service is not configured."""


@runtime_checkable
class EmailService(Protocol):
    """Sends an :class:`EmailMessage`."""

    def send(self, message: EmailMessage) -> None:
        ...


def _split_emails(value: str | None) -> list[str]:
    """Parse a comma-separated address string into a list (CC may hold several)."""
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def recipients_from_settings(settings: Settings) -> tuple[list[str], list[str]]:
    """Return ``(to, cc)`` address lists from settings (To: Alex, CC: Sagy)."""
    to = _split_emails(settings.hw_to_email)
    cc = _split_emails(settings.hw_cc_email)
    if not to:
        raise EmailSendError("HW_TO_EMAIL is not configured.")
    return to, cc


class RecordingEmailService:
    """A fake email service that records messages instead of sending them."""

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


class GmailEmailService:
    """Sends mail through the Gmail API using the project's Google OAuth creds."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._service: Any = None

    def _client(self) -> Any:  # pragma: no cover - needs live credentials
        if self._service is not None:
            return self._service
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        s = self._settings
        if not (
            s.google_oauth_client_id
            and s.google_oauth_client_secret
            and s.google_oauth_refresh_token
        ):
            raise EmailSendError("Google OAuth credentials are not fully configured.")
        creds = Credentials(  # type: ignore[no-untyped-call]
            token=None,
            refresh_token=s.google_oauth_refresh_token.get_secret_value(),
            client_id=s.google_oauth_client_id,
            client_secret=s.google_oauth_client_secret.get_secret_value(),
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/gmail.send"],
        )
        self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return self._service

    def send(self, message: EmailMessage) -> None:  # pragma: no cover - live only
        import base64
        from email.message import EmailMessage as MimeMessage

        mime = MimeMessage()
        mime["To"] = ", ".join(message.to)
        if message.cc:
            mime["Cc"] = ", ".join(message.cc)
        mime["Subject"] = message.subject
        mime.set_content(message.body)
        for attachment in message.attachments:
            if attachment.content is not None:
                mime.add_attachment(
                    attachment.content,
                    maintype="application",
                    subtype="octet-stream",
                    filename=attachment.filename,
                )
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
        try:
            self._client().users().messages().send(userId="me", body={"raw": raw}).execute()
        except Exception as exc:  # noqa: BLE001 - surface a uniform send error
            raise EmailSendError(f"Failed to send email: {exc}") from exc


def build_email_service(settings: Settings) -> EmailService:
    """Construct the configured email service (Gmail for production)."""
    return GmailEmailService(settings)
