"""Tests for the validated data layer (app/services/data_access.py)."""
from __future__ import annotations

import json

import pytest

from app.services import data_access as da
from app.services.data_access import DataAccessError


def test_load_deploys_valid():
    rows = da.load_deploys()
    assert len(rows) >= 1
    assert da.DEPLOYS_COLUMNS <= set(rows[0].keys())


def test_load_service_catalog_valid():
    catalog = da.load_service_catalog()
    names = {s["name"] for s in catalog["services"]}
    assert {"postgres", "auth-api", "api-gateway"} <= names


def test_load_impact_matrix_valid():
    rows = da.load_impact_matrix()
    assert any(r["service"] == "postgres" and r["severity"] == "P2" for r in rows)


def test_load_incident_history_has_new_columns():
    rows = da.load_incident_history()
    assert len(rows) >= 30
    assert {"environment", "resolution"} <= set(rows[0].keys())


def test_load_external_status_valid():
    status = da.load_external_status()
    assert isinstance(status["providers"], list)
    assert any(p["name"] == "backup-psp" for p in status["providers"])


def test_incident_history_summary_aggregates():
    summary = da.incident_history_summary()
    assert summary["total_incidents"] >= 30
    assert "postgres" in summary["by_service"]
    assert summary["by_service"]["postgres"]["count"] >= 1


def test_missing_csv_raises(tmp_path):
    with pytest.raises(DataAccessError):
        da.load_deploys(data_dir=str(tmp_path))


def test_missing_columns_raises(tmp_path):
    bad = tmp_path / "deploys.csv"
    bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(DataAccessError) as exc:
        da._read_csv_rows(bad, da.DEPLOYS_COLUMNS)
    assert "missing required columns" in str(exc.value)


def test_malformed_json_raises(tmp_path):
    bad = tmp_path / "service_catalog.json"
    bad.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(DataAccessError) as exc:
        da.load_service_catalog(data_dir=str(tmp_path))
    assert "Malformed JSON" in str(exc.value)


def test_json_wrong_shape_raises(tmp_path):
    bad = tmp_path / "external_status.json"
    bad.write_text(json.dumps({"nope": []}), encoding="utf-8")
    with pytest.raises(DataAccessError):
        da.load_external_status(data_dir=str(tmp_path))
