"""Session debug logging for agent debug mode (NDJSON to workspace log + optional ingest)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SESSION_ID = "9dab18"
_INGEST_URL = "http://127.0.0.1:7343/ingest/c2d45c21-7b99-4fcd-9cae-c1134bf94229"
_HOST_INGEST_URL = "http://host.docker.internal:7343/ingest/c2d45c21-7b99-4fcd-9cae-c1134bf94229"
_LOG_CANDIDATES = (
    Path(__file__).resolve().parent.parent.parent / "debug-9dab18.log",
    Path(__file__).resolve().parent.parent.parent.parent / "debug-9dab18.log",
)


def agent_log(
    location: str,
    message: str,
    data: dict[str, Any],
    hypothesis_id: str,
    run_id: str = "pre-fix",
) -> None:
    """Append one NDJSON debug line; best-effort POST to debug ingest."""
    payload = {
        "sessionId": _SESSION_ID,
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "hypothesisId": hypothesis_id,
        "runId": run_id,
    }
    line = json.dumps(payload, default=str) + "\n"
    for path in _LOG_CANDIDATES:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as fh:
                fh.write(line)
            break
        except OSError:
            continue
    body = json.dumps(payload, default=str).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Debug-Session-Id": _SESSION_ID,
    }
    for url in (_INGEST_URL, _HOST_INGEST_URL):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            urllib.request.urlopen(req, timeout=0.5)
            break
        except (urllib.error.URLError, TimeoutError, OSError):
            continue
