"""Quick smoke test for deployed IncidentIQ API surface (run inside container or locally)."""

from __future__ import annotations

import sys

from fastapi.testclient import TestClient

from app.main import app


def main() -> int:
    failed: list[str] = []
    with TestClient(app) as client:
        checks = [
            ("GET /health", lambda: client.get("/health").status_code == 200),
            ("GET /api/bootstrap", lambda: "stats" in client.get("/api/bootstrap").json()),
            ("GET /api/incidents", lambda: client.get("/api/incidents").status_code == 200),
            ("GET /", lambda: client.get("/").status_code == 200),
            ("POST /api/query 422", lambda: client.post("/api/query", json={"question": "ab"}).status_code == 422),
            (
                "GET /static/app.js cache",
                lambda: "Cache-Control" in client.get("/static/app.js").headers,
            ),
        ]
        for name, fn in checks:
            try:
                ok = bool(fn())
            except Exception as exc:  # noqa: BLE001
                ok = False
                print(f"FAIL {name}: {exc}")
            if ok:
                print(f"PASS {name}")
            else:
                print(f"FAIL {name}")
                failed.append(name)
    if failed:
        print(f"Smoke failed: {len(failed)} check(s)")
        return 1
    print("Smoke passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
