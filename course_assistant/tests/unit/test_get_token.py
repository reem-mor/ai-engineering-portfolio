"""Test the pure part of the Google OAuth token helper."""

from __future__ import annotations

from course_assistant.scripts.get_google_token import SCOPES, build_client_config


def test_scopes_cover_drive_and_gmail() -> None:
    assert "https://www.googleapis.com/auth/drive.readonly" in SCOPES
    assert "https://www.googleapis.com/auth/gmail.send" in SCOPES


def test_build_client_config_shape() -> None:
    config = build_client_config("cid", "secret")
    installed = config["installed"]
    assert installed["client_id"] == "cid"
    assert installed["client_secret"] == "secret"
    assert installed["token_uri"] == "https://oauth2.googleapis.com/token"
    assert "http://localhost" in installed["redirect_uris"]  # type: ignore[operator]
