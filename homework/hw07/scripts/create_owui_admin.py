#!/usr/bin/env python3
"""Create or reset the Open WebUI admin account (no secrets printed)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from env_loader import load_hw07_env  # noqa: E402

load_hw07_env()


def signup(base: str, name: str, email: str, password: str) -> str:
    """Register first admin user; returns JWT token."""
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{base.rstrip('/')}/api/v1/auths/signup",
            json={"name": name, "email": email, "password": password},
        )
        if response.status_code == 200:
            token = response.json().get("token", "")
            if not token:
                raise RuntimeError("Signup succeeded but no token returned.")
            return token
        if response.status_code in {400, 403}:
            # Instance already has users — fall back to signin + password reset via container
            raise RuntimeError(
                "Signup rejected (users may already exist). "
                "Use reset_webui_password.py or wipe the open-webui volume."
            )
        response.raise_for_status()
        return ""


def signin(base: str, email: str, password: str) -> str:
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{base.rstrip('/')}/api/v1/auths/signin",
            json={"email": email, "password": password},
        )
        response.raise_for_status()
        token = response.json().get("token", "")
        if not token:
            raise RuntimeError("Sign-in succeeded but no token returned.")
        return token


def main() -> int:
    parser = argparse.ArgumentParser(description="Create OWUI admin on fresh install.")
    parser.add_argument("--url", default=os.getenv("OWUI_URL", "http://localhost:3000"))
    parser.add_argument("--name", default=os.getenv("OWUI_NAME", "Re'em Mor"))
    parser.add_argument("--email", default=os.getenv("OWUI_EMAIL", ""))
    parser.add_argument("--password", default=os.getenv("OWUI_PASSWORD", ""))
    parser.add_argument(
        "--signup-only",
        action="store_true",
        help="Fail if signup is not available (fresh volume).",
    )
    args = parser.parse_args()

    if not args.email or not args.password:
        print(
            "ERROR: set OWUI_EMAIL and OWUI_PASSWORD env vars (never commit passwords).",
            file=sys.stderr,
        )
        return 2

    try:
        token = signup(args.url, args.name, args.email, args.password)
        print(f"OK: signed up admin {args.email}")
    except RuntimeError as exc:
        if args.signup_only:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(f"NOTE: {exc}; trying sign-in instead.")
        token = signin(args.url, args.email, args.password)
        print(f"OK: signed in as {args.email}")

    # Verify admin can reach knowledge API
    with httpx.Client(timeout=30.0) as client:
        response = client.get(
            f"{args.url.rstrip('/')}/api/v1/knowledge/",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
    print("OK: admin API access verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
