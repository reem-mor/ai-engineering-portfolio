"""Load static UI data from app/data/*.json."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_json(name: str) -> Any:
    return json.loads((_DATA_DIR / name).read_text(encoding="utf-8"))


@lru_cache
def load_example_questions() -> list[dict[str, str]]:
    return _load_json("example_questions.json")


@lru_cache
def load_workflow_alerts() -> list[dict[str, Any]]:
    return _load_json("workflow_alerts.json")


def flat_example_questions() -> list[str]:
    return [item["question"] for item in load_example_questions()]


def find_workflow_alert(alert_id: str | None) -> dict[str, Any] | None:
    if not alert_id:
        return None
    return next((a for a in load_workflow_alerts() if a.get("id") == alert_id), None)
