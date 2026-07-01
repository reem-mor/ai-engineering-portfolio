"""Pytest configuration for hw07 — adds project root to import path."""

from __future__ import annotations

import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from e2e.open_webui_client import OpenWebUIClient


@pytest.fixture(scope="session")
def api_client() -> Iterator[OpenWebUIClient]:
    """Single sign-in per session to avoid Open WebUI auth rate limits."""
    client = OpenWebUIClient()
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            client.sign_in()
            last_error = None
            break
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code == 429 and attempt < 3:
                time.sleep(5 * (attempt + 1))
                continue
            raise
    if last_error:
        raise last_error
    yield client
    client.close()
