"""Load hw07 configuration: repo root .env first, optional local overrides second."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

HW07_ROOT = Path(__file__).resolve().parent
REPO_ROOT = HW07_ROOT.parent.parent


def load_hw07_env() -> None:
    """Load secrets from repo root .env; fill gaps from homework/hw07/.env."""
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(HW07_ROOT / ".env")
