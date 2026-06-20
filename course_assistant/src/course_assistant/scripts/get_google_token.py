"""One-time helper to obtain a Google OAuth refresh token.

Runs the installed-app OAuth flow for the scopes the bot needs (Drive read-only +
Gmail send) and prints the resulting refresh token to paste into ``.env`` as
``GOOGLE_OAUTH_REFRESH_TOKEN``.

Usage (run on a machine with a browser):

    # using GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET from the env:
    uv run course-assistant-get-token

    # or with a Desktop-app client_secret.json downloaded from Google Cloud:
    uv run course-assistant-get-token --client-secrets client_secret.json
"""

from __future__ import annotations

import argparse
import json
import os

# A single token covering both features the bot uses.
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def build_client_config(client_id: str, client_secret: str) -> dict[str, dict[str, object]]:
    """Build an installed-app client config dict from a client id/secret."""
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def _run_flow(args: argparse.Namespace) -> None:  # pragma: no cover - interactive/browser
    from google_auth_oauthlib.flow import InstalledAppFlow

    if args.client_secrets:
        with open(args.client_secrets, encoding="utf-8") as fh:
            client_config = json.load(fh)
    else:
        client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
        client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")
        if not (client_id and client_secret):
            raise SystemExit(
                "Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET, "
                "or pass --client-secrets <path to Desktop client_secret.json>."
            )
        client_config = build_client_config(client_id, client_secret)

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n✅ Success. Add this to your .env:\n")
    print(f"GOOGLE_OAUTH_REFRESH_TOKEN={creds.refresh_token}")
    if not args.client_secrets:
        print("\n(GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET are already set.)")


def main() -> None:  # pragma: no cover - entry point
    parser = argparse.ArgumentParser(description="Obtain a Google OAuth refresh token.")
    parser.add_argument(
        "--client-secrets",
        help="Path to a Desktop-app client_secret.json (otherwise read client id/secret from env).",
    )
    _run_flow(parser.parse_args())


if __name__ == "__main__":  # pragma: no cover
    main()
