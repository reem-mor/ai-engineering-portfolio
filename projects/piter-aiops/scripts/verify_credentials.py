#!/usr/bin/env python3
"""Verify credential layout without printing secrets.

Checks:
  - projects/piter-aiops/.env has required PITER_* vars when Bedrock is enabled
  - AWS_PROFILE in .env matches a stanza in ~/.aws/credentials (if profile set)
  - Config.from_env() loads (when Bedrock enabled)
  - Optional: aws sts get-caller-identity for the configured profile

Usage (from projects/piter-aiops):
  python scripts/verify_credentials.py
  python scripts/verify_credentials.py --sts
"""
from __future__ import annotations

import argparse
import configparser
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
CREDS_PATH = Path.home() / ".aws" / "credentials"

REQUIRED_BEDROCK = (
    "PITER_AWS_REGION",
    "PITER_BEDROCK_KB_ID",
    "PITER_BEDROCK_MODEL_ARN",
    "PITER_FLASK_SECRET_KEY",
    "PITER_USE_BEDROCK",
)


def _load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def _truthy(raw: str) -> bool:
    return raw.lower() in {"true", "1", "yes", "on"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify PITER AiOps credential layout")
    parser.add_argument(
        "--sts",
        action="store_true",
        help="Run aws sts get-caller-identity for AWS_PROFILE",
    )
    args = parser.parse_args()
    errors: list[str] = []

    if not ENV_PATH.is_file():
        errors.append(f"Missing {ENV_PATH} — copy from .env.example")
        _report(errors)
        return 1

    env = _load_dotenv(ENV_PATH)
    use_bedrock = _truthy(env.get("PITER_USE_BEDROCK", env.get("USE_BEDROCK", "false")))

    if use_bedrock:
        for key in REQUIRED_BEDROCK:
            if not env.get(key):
                errors.append(f".env missing or empty: {key}")
        rag = env.get("RAG_BACKEND", "agent")
        if rag == "agent":
            for key in ("PITER_BEDROCK_AGENT_ID", "PITER_BEDROCK_AGENT_ALIAS_ID"):
                if not env.get(key):
                    errors.append(f"RAG_BACKEND=agent requires {key}")

    profile = env.get("AWS_PROFILE", "").strip()
    if use_bedrock and profile:
        if not CREDS_PATH.is_file():
            errors.append(f"AWS_PROFILE={profile!r} but {CREDS_PATH} not found")
        else:
            cp = configparser.ConfigParser()
            cp.read(CREDS_PATH)
            if profile not in cp.sections():
                errors.append(
                    f"AWS_PROFILE={profile!r} not found in {CREDS_PATH} "
                    f"(sections: {', '.join(cp.sections()) or 'none'})"
                )

    if use_bedrock and not errors:
        os.chdir(ROOT)
        sys.path.insert(0, str(ROOT))
        try:
            from app.config import Config

            Config.from_env()
            print("OK: Config.from_env()")
        except Exception as exc:
            errors.append(f"Config.from_env() failed: {exc}")

    if args.sts and profile and not errors:
        proc = subprocess.run(
            ["aws", "sts", "get-caller-identity", "--profile", profile, "--output", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(f"aws sts failed for profile {profile!r}: {proc.stderr.strip()}")
        else:
            print(f"OK: aws sts get-caller-identity --profile {profile}")

    _report(errors)
    return 1 if errors else 0


def _report(errors: list[str]) -> None:
    if errors:
        print("FAIL:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("PASS: credential layout looks correct")
        print(f"  env file: {ENV_PATH}")
        print(f"  aws creds: {CREDS_PATH}")


if __name__ == "__main__":
    raise SystemExit(main())
