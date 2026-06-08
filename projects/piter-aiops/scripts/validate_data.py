#!/usr/bin/env python3
"""Validate PITER AiOps CSV/JSON demo data."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CSV_SCHEMAS = {
    "deployments.csv": {
        "deployment_id",
        "service",
        "environment",
        "version",
        "deployed_at",
        "status",
        "owner",
        "change_summary",
    },
    "historical_incidents.csv": {
        "incident_id",
        "service",
        "environment",
        "severity",
        "symptom",
        "root_cause",
        "resolution",
        "business_impact",
        "occurred_at",
    },
}

JSON_SCHEMAS = {
    "services.json": ("services", list),
    "escalation_rules.json": ("rules", list),
    "demo_questions.json": (None, list),
    "tool_test_cases.json": (None, list),
    "sample_alerts.json": (None, list),
}


class ValidationError(RuntimeError):
    """Raised when data validation fails."""


def _validate_csv(name: str, required: set[str]) -> None:
    path = DATA / name
    if not path.is_file():
        raise ValidationError(f"Missing CSV file: {path}")
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = required - set(frame.columns)
    if missing:
        raise ValidationError(f"{name} missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValidationError(f"{name} must contain at least one row")
    empty_required = [
        column
        for column in required
        if frame[column].astype(str).str.strip().eq("").any()
    ]
    if empty_required:
        raise ValidationError(f"{name} has empty required values: {sorted(empty_required)}")


def _validate_json(name: str, key: str | None, expected_type: type) -> Any:
    path = DATA / name
    if not path.is_file():
        raise ValidationError(f"Missing JSON file: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{name} is invalid JSON: {exc}") from exc
    value = data if key is None else data.get(key)
    if not isinstance(value, expected_type):
        target = "top-level value" if key is None else f"{key!r}"
        raise ValidationError(f"{name} {target} must be {expected_type.__name__}")
    if hasattr(value, "__len__") and len(value) == 0:
        raise ValidationError(f"{name} must not be empty")
    return data


def validate() -> list[str]:
    messages: list[str] = []
    for name, required in CSV_SCHEMAS.items():
        _validate_csv(name, required)
        messages.append(f"OK CSV {name}")
    parsed_json = {}
    for name, (key, expected_type) in JSON_SCHEMAS.items():
        parsed_json[name] = _validate_json(name, key, expected_type)
        messages.append(f"OK JSON {name}")

    services = {
        item["service"]
        for item in parsed_json["services.json"]["services"]
        if isinstance(item, dict) and item.get("service")
    }
    if "auth-service" not in services:
        raise ValidationError("services.json must include auth-service")
    for rule in parsed_json["escalation_rules.json"]["rules"]:
        for field in ("priority", "condition", "escalation_target", "channel", "response_time", "message_template"):
            if not str(rule.get(field, "")).strip():
                raise ValidationError(f"escalation_rules.json rule missing {field}")
    return messages


def main() -> int:
    try:
        for message in validate():
            print(message)
    except ValidationError as exc:
        print(f"DATA VALIDATION FAILED: {exc}")
        return 1
    print("PITER data validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
