"""
End-to-end verification against a running Flask app (default http://localhost:8080).

Usage:
    py -3.12 scripts/verify_e2e.py
    APP_URL=http://127.0.0.1:8080 py -3.12 scripts/verify_e2e.py
"""
from __future__ import annotations

import http.cookiejar
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

APP_URL = os.environ.get("APP_URL", "http://localhost:8080").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "sample_documents"
REQUIRED_EXTENSIONS = {".md", ".txt", ".csv", ".docx", ".pdf"}


class Session:
    def __init__(self) -> None:
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.csrf: str | None = None

    def get(self, path: str) -> tuple[int, str]:
        req = urllib.request.Request(f"{APP_URL}{path}", method="GET")
        with self.opener.open(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            self._capture_csrf(body)
            return resp.status, body

    def post_json(self, path: str, payload: dict) -> tuple[int, dict | str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.csrf:
            headers["X-CSRFToken"] = self.csrf
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{APP_URL}{path}", data=body, method="POST", headers=headers)
        try:
            with self.opener.open(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                return exc.code, json.loads(raw)
            except json.JSONDecodeError:
                return exc.code, raw

    def post_form(self, path: str, fields: dict[str, str], *, htmx: bool = False) -> tuple[int, str]:
        if self.csrf:
            fields = {**fields, "csrf_token": self.csrf}
        data = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if htmx:
            headers["HX-Request"] = "true"
            headers["Accept"] = "text/html"
        req = urllib.request.Request(f"{APP_URL}{path}", data=data, method="POST", headers=headers)
        try:
            with self.opener.open(req, timeout=120) as resp:
                return resp.status, resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")

    def _capture_csrf(self, html: str) -> None:
        match = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
        if match:
            self.csrf = match.group(1)


def check(name: str, ok: bool, detail: str = "") -> bool:
    tag = "PASS" if ok else "FAIL"
    line = f"[{tag}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)
    return ok


def main() -> int:
    passed = 0
    total = 0
    session = Session()

    def record(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed, total
        total += 1
        if check(name, ok, detail):
            passed += 1

    try:
        status, body = session.get("/health")
        record("GET /health", status == 200 and '"ok"' in body, body.strip())
    except Exception as exc:
        record("GET /health", False, str(exc))
        print(f"\nApp not reachable at {APP_URL}. Start with: docker compose up -d --build")
        return 1

    try:
        _, html = session.get("/")
        record("CSRF token loaded", bool(session.csrf))
        for marker in ('id="mvp"', 'id="architecture"', 'id="live-kb"', "IncidentIQ", "topnav"):
            record(f"Homepage contains {marker!r}", marker in html)
    except Exception as exc:
        record("GET /", False, str(exc))

    found_ext = {p.suffix.lower() for p in CORPUS.iterdir() if p.is_file()}
    for ext in sorted(REQUIRED_EXTENSIONS):
        record(f"Corpus has {ext} file", ext in found_ext)

    cases = [
        ("empty question", "", 400, "empty_question"),
        ("short question", "ab", 400, "short_question"),
        ("stopwords only", "what is the", 400, "stopwords_only"),
        ("oversize question", "x" * 501, 400, "oversize_question"),
    ]
    for label, question, expect_status, expect_reason in cases:
        status, data = session.post_json("/ask?format=json", {"question": question})
        ok = (
            status == expect_status
            and isinstance(data, dict)
            and data.get("ok") is False
            and data.get("reason") == expect_reason
        )
        reason = data.get("reason") if isinstance(data, dict) else str(data)[:80]
        record(f"JSON validation: {label}", ok, f"status={status} reason={reason}")

    status, data = session.post_json(
        "/ask?format=json",
        {"question": "How do I triage an authentication service incident?"},
    )
    record(
        "JSON grounded answer",
        status == 200
        and isinstance(data, dict)
        and data.get("ok") is True
        and data.get("grounded") is True
        and data.get("citations")
        and data["citations"][0].get("source_label"),
        f"latency={data.get('latency_ms') if isinstance(data, dict) else 'n/a'}ms",
    )

    status, data = session.post_json(
        "/ask?format=json",
        {"question": "What is the best restaurant in Tokyo?"},
    )
    record(
        "JSON off-topic refusal",
        status == 200 and isinstance(data, dict) and data.get("grounded") is False,
    )

    status, html = session.post_form(
        "/ask",
        {"question": "How do I triage an authentication service incident?"},
        htmx=True,
    )
    record(
        "HTMX /ask returns HTML partial",
        status == 200 and "badge-grounded" in html,
    )
    record("HTMX answer has citation list", "citation-list" in html)

    status, html = session.post_form(
        "/workflow/triage",
        {
            "alert_id": "A-2041",
            "question": "postgres connection pool exhausted — which runbook applies?",
        },
        htmx=True,
    )
    record(
        "Workflow triage partial",
        status == 200 and "workflow-result" in html,
    )

    print(f"\n{passed}/{total} checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
