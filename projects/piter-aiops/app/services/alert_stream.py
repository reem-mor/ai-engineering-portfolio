"""Load and summarize the deterministic alert storm CSV for demo APIs."""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STREAM_PATH = ROOT / "data" / "source" / "alert_stream.csv"

WARNING_SHOT_PREFIX = "ALT-DEMO-WARN-"


@lru_cache(maxsize=1)
def _load_rows(path: str | None = None) -> tuple[dict[str, str], ...]:
    csv_path = Path(path) if path else DEFAULT_STREAM_PATH
    if not csv_path.is_file():
        return ()
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return tuple(dict(row) for row in csv.DictReader(handle))


def load_alert_stream(path: str | None = None) -> list[dict[str, str]]:
    return list(_load_rows(path))


def summarize_alert_stream(path: str | None = None) -> dict:
    rows = load_alert_stream(path)
    by_severity: dict[str, int] = {}
    for row in rows:
        sev = row.get("severity", "P4")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    noise_count = by_severity.get("P3", 0) + by_severity.get("P4", 0)
    p1_rows = [r for r in rows if r.get("severity") == "P1" or r.get("is_trigger") == "true"]
    warning_rows = [r for r in rows if str(r.get("alert_id", "")).startswith(WARNING_SHOT_PREFIX)]

    return {
        "total": len(rows),
        "label": f"Alert storm corpus ({len(rows)} alerts)",
        "duration_seconds": 300,
        "by_severity": by_severity,
        "noise_suppressed": noise_count,
        "warning_signals": len(warning_rows),
        "p1_trigger": p1_rows[0] if p1_rows else None,
        "p1_count": len(p1_rows),
    }


def p1_demo_alert(path: str | None = None) -> dict:
    """Build a triage payload from the deterministic P1 trigger row."""
    summary = summarize_alert_stream(path)
    trigger = summary.get("p1_trigger") or {}
    if not trigger:
        return {
            "alert_id": "ALT-DEMO-P1-001",
            "service": "bet-service",
            "environment": "GIB-UKGC",
            "severity": "P1",
            "symptom": "CRITICAL: bet-service nodes unresponsive — 100% error rate on GIB-UKGC",
            "description": "CRITICAL: bet-service nodes unresponsive — 100% error rate on GIB-UKGC",
            "alert_time": "2026-06-10T10:02:55.000Z",
            "duration_minutes": 45,
        }
    return {
        "alert_id": trigger.get("alert_id", "ALT-DEMO-P1-001"),
        "service": trigger.get("service", "bet-service"),
        "environment": trigger.get("environment", "GIB-UKGC"),
        "severity": trigger.get("severity", "P1"),
        "symptom": trigger.get("title", trigger.get("symptom", "")),
        "description": trigger.get("title", trigger.get("description", "")),
        "alert_time": trigger.get("timestamp", "2026-06-10T10:02:55.000Z"),
        "duration_minutes": 45,
    }
