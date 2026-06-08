"""Typed, validated loaders for the PITER AiOps data layer (Pandas + CSV + JSON).

Centralizes access to the CSV/JSON operational datasets so the tools and the
local agent share one schema-validated source of truth. Each loader raises a
clear :class:`DataAccessError` on a missing file, missing column, or malformed
JSON/CSV instead of leaking a raw traceback.

Pandas is the preferred CSV engine and is used whenever it is importable
(Docker/Linux/CI). On hardened hosts where the compiled numpy/pandas binaries
are blocked, the loaders fall back to the standard-library ``csv`` module and
return the same ``list[dict]`` shape, so the local demo and tests never break.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_AGENT_DATA = _PROJECT_ROOT / "data" / "agent_data"
_SOURCE_DATA = _PROJECT_ROOT / "data" / "source"
_DATA_ROOT = _PROJECT_ROOT / "data"
_KB_RUNBOOKS = _PROJECT_ROOT / "knowledge_base" / "runbooks"
_HISTORY = _PROJECT_ROOT / "data" / "sample_documents" / "incident_history.csv"

DEPLOYS_COLUMNS = {
    "deploy_id",
    "service",
    "environment",
    "version",
    "deployed_at",
    "deployed_by",
    "change_summary",
}
IMPACT_COLUMNS = {
    "environment",
    "service",
    "severity",
    "tier",
    "revenue_impact_usd_per_hour",
    "player_impact_pct",
    "regulatory_flag",
    "escalation_minutes",
}
HISTORY_COLUMNS = {
    "incident_id",
    "date",
    "severity",
    "service",
    "root_cause",
    "mttr_minutes",
    "customer_impact",
    "environment",
    "resolution",
}

SOURCE_DEPLOYS_COLUMNS = {
    "deploy_id",
    "timestamp",
    "environment",
    "service",
    "version",
    "status",
    "change_summary",
    "risk_level",
    "rollback_available",
}
SERVICE_OWNERS_COLUMNS = {
    "service",
    "owning_team",
    "service_tier",
    "business_function",
    "slack_channel",
    "primary_on_call_role",
    "secondary_on_call_role",
    "runbook",
    "dashboard",
    "dependencies",
    "regulatory_exposure",
}
PAST_INCIDENTS_COLUMNS = {
    "incident_id",
    "service",
    "environment",
    "severity",
    "root_cause",
    "resolution",
    "mttr_minutes",
    "lessons_learned",
    "related_runbook",
}
ALERT_STREAM_COLUMNS = {
    "alert_id",
    "timestamp",
    "environment",
    "service",
    "severity",
    "title",
}
SOURCE_ALERTS_COLUMNS = {
    "alert_id",
    "timestamp",
    "environment",
    "service",
    "severity",
    "title",
}


class DataAccessError(RuntimeError):
    """Raised when a dataset is missing, malformed, or fails schema validation."""


# Memoize the pandas import. On hardened hosts the blocked numpy DLL makes each
# import attempt slow, so we try exactly once per process. ``False`` means
# "tried and unavailable"; ``None`` means "not tried yet".
_PANDAS_MODULE: Any = None
_PANDAS_TRIED = False


def _get_pandas():
    """Return the pandas module if importable here, else ``None`` (memoized)."""
    global _PANDAS_MODULE, _PANDAS_TRIED
    if not _PANDAS_TRIED:
        _PANDAS_TRIED = True
        try:
            import pandas as pd  # noqa: WPS433 — optional, lazily imported once
        except ImportError:
            _PANDAS_MODULE = None
        else:
            _PANDAS_MODULE = pd
    return _PANDAS_MODULE


def pandas_available() -> bool:
    """Return True when pandas (and its numpy backend) can be imported here."""
    return _get_pandas() is not None


def _read_csv_rows(path: Path, required: set[str]) -> list[dict[str, str]]:
    """Read a CSV into a list of dict rows, validating required columns.

    Uses pandas when available, otherwise the stdlib ``csv`` module. Both paths
    return identical ``list[dict[str, str]]`` output.
    """
    if not path.is_file():
        raise DataAccessError(f"Missing data file: {path.name}")
    pd = _get_pandas()
    if pd is None:
        return _read_csv_stdlib(path, required)

    try:
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError as exc:
        raise DataAccessError(f"Data file is empty: {path.name}") from exc
    except pd.errors.ParserError as exc:
        raise DataAccessError(f"Malformed CSV: {path.name} ({exc})") from exc
    missing = required - set(frame.columns)
    if missing:
        raise DataAccessError(
            f"{path.name} is missing required columns: {sorted(missing)}"
        )
    return frame.to_dict("records")


def _read_csv_stdlib(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise DataAccessError(f"Data file is empty: {path.name}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise DataAccessError(
                f"{path.name} is missing required columns: {sorted(missing)}"
            )
        return [dict(row) for row in reader]


def _read_json(path: Path) -> Any:
    if not path.is_file():
        raise DataAccessError(f"Missing data file: {path.name}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DataAccessError(f"Malformed JSON: {path.name} ({exc})") from exc


def load_deploys(data_dir: str | Path | None = None) -> list[dict[str, str]]:
    """Return deployments as validated dict rows."""
    base = Path(data_dir) if data_dir else _AGENT_DATA
    return _read_csv_rows(base / "deploys.csv", DEPLOYS_COLUMNS)


def load_service_catalog(data_dir: str | Path | None = None) -> dict[str, Any]:
    """Return the service catalog dict, validating the top-level shape."""
    base = Path(data_dir) if data_dir else _AGENT_DATA
    catalog = _read_json(base / "service_catalog.json")
    if not isinstance(catalog, dict) or "services" not in catalog:
        raise DataAccessError("service_catalog.json must contain a 'services' list")
    if not isinstance(catalog["services"], list):
        raise DataAccessError("service_catalog.json 'services' must be a list")
    return catalog


def load_impact_matrix(data_dir: str | Path | None = None) -> list[dict[str, str]]:
    """Return the impact matrix as validated dict rows."""
    base = Path(data_dir) if data_dir else _AGENT_DATA
    return _read_csv_rows(base / "impact_matrix.csv", IMPACT_COLUMNS)


def load_incident_history(history_path: str | Path | None = None) -> list[dict[str, str]]:
    """Return incident history as validated dict rows."""
    path = Path(history_path) if history_path else _HISTORY
    return _read_csv_rows(path, HISTORY_COLUMNS)


def load_external_status(data_dir: str | Path | None = None) -> dict[str, Any]:
    """Return external dependency status, validating the top-level shape."""
    base = Path(data_dir) if data_dir else _DATA_ROOT
    status = _read_json(base / "external_status.json")
    if not isinstance(status, dict) or "providers" not in status:
        raise DataAccessError("external_status.json must contain a 'providers' list")
    if not isinstance(status["providers"], list):
        raise DataAccessError("external_status.json 'providers' must be a list")
    return status


def incident_history_summary(history_path: str | Path | None = None) -> dict[str, Any]:
    """Aggregate incident history into per-service counts and mean MTTR.

    Demonstrates pandas-based processing when pandas is available; falls back to
    a pure-Python aggregation otherwise. Returns identical output either way.
    """
    rows = load_incident_history(history_path)
    pd = _get_pandas()
    if pd is None:
        return _summary_stdlib(rows)

    frame = pd.DataFrame(rows)
    frame = frame.assign(
        mttr_minutes=pd.to_numeric(frame["mttr_minutes"], errors="coerce")
    )
    grouped = frame.groupby("service")["mttr_minutes"].agg(["count", "mean"])
    return {
        "total_incidents": int(len(frame)),
        "by_service": {
            service: {
                "count": int(stats["count"]),
                "avg_mttr_minutes": round(float(stats["mean"]), 1),
            }
            for service, stats in grouped.iterrows()
        },
    }


def source_data_dir() -> Path:
    """Return the canonical structured dataset directory."""
    return _SOURCE_DATA


def list_runbook_files() -> set[str]:
    """Return runbook filenames present under knowledge_base/runbooks/."""
    if not _KB_RUNBOOKS.is_dir():
        return set()
    return {
        path.name
        for path in _KB_RUNBOOKS.iterdir()
        if path.is_file() and path.suffix == ".md" and path.name != "README.md"
    }


def load_source_alert_stream(source_dir: str | Path | None = None) -> list[dict[str, str]]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    return _read_csv_rows(base / "alert_stream.csv", ALERT_STREAM_COLUMNS)


def load_source_alerts(source_dir: str | Path | None = None) -> list[dict[str, str]]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    return _read_csv_rows(base / "alerts.csv", SOURCE_ALERTS_COLUMNS)


def load_service_owners(source_dir: str | Path | None = None) -> list[dict[str, str]]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    return _read_csv_rows(base / "service_owners.csv", SERVICE_OWNERS_COLUMNS)


def load_source_deploys(source_dir: str | Path | None = None) -> list[dict[str, str]]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    return _read_csv_rows(base / "deploys.csv", SOURCE_DEPLOYS_COLUMNS)


def load_business_impact(source_dir: str | Path | None = None) -> dict[str, Any]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    data = _read_json(base / "business_impact.json")
    if not isinstance(data, dict) or "services" not in data:
        raise DataAccessError("business_impact.json must contain a 'services' object")
    return data


def load_priority_matrix(source_dir: str | Path | None = None) -> dict[str, Any]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    data = _read_json(base / "priority_matrix.json")
    if not isinstance(data, dict) or "thresholds" not in data:
        raise DataAccessError("priority_matrix.json must contain 'thresholds'")
    return data


def load_escalation_policies(source_dir: str | Path | None = None) -> dict[str, Any]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    data = _read_json(base / "escalation_policies.json")
    if not isinstance(data, dict) or "default_policy" not in data:
        raise DataAccessError("escalation_policies.json must contain 'default_policy'")
    return data


def load_past_incidents(source_dir: str | Path | None = None) -> list[dict[str, str]]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    return _read_csv_rows(base / "past_incidents.csv", PAST_INCIDENTS_COLUMNS)


def load_on_call_schedule(source_dir: str | Path | None = None) -> list[dict[str, str]]:
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    path = base / "on_call_schedule.csv"
    if not path.is_file():
        raise DataAccessError("Missing data file: on_call_schedule.csv")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def resolve_alert(
    *,
    alert_id: str = "",
    service: str = "",
    environment: str = "",
    source_dir: str | Path | None = None,
) -> dict[str, str] | None:
    """Resolve an alert from alert_stream, summary alerts, or service+env match."""
    base = Path(source_dir) if source_dir else _SOURCE_DATA
    aid = (alert_id or "").strip()
    svc = (service or "").strip().lower()
    env = (environment or "").strip().upper()

    if aid:
        for row in load_source_alert_stream(base):
            if row.get("alert_id") == aid:
                return dict(row)
        for row in load_source_alerts(base):
            if row.get("alert_id") == aid:
                return dict(row)

    if svc and env:
        for row in load_source_alert_stream(base):
            if (
                row.get("service", "").lower() == svc
                and row.get("environment", "").upper() == env
                and row.get("is_trigger", "").lower() == "true"
            ):
                return dict(row)
        for row in load_source_alerts(base):
            if (
                row.get("service", "").lower() == svc
                and row.get("environment", "").upper() == env
            ):
                return dict(row)

    return None


def _summary_stdlib(rows: list[dict[str, str]]) -> dict[str, Any]:
    by_service: dict[str, list[int]] = {}
    for row in rows:
        try:
            mttr = int(row["mttr_minutes"])
        except (KeyError, ValueError):
            continue
        by_service.setdefault(row["service"], []).append(mttr)
    return {
        "total_incidents": len(rows),
        "by_service": {
            service: {
                "count": len(values),
                "avg_mttr_minutes": round(sum(values) / len(values), 1),
            }
            for service, values in by_service.items()
        },
    }
