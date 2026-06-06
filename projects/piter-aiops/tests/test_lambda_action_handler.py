"""Unit tests for the IncidentIQ ops Lambda action group handler."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LAMBDA_DIR = ROOT / "action_groups" / "incidentiq-ops"
sys.path.insert(0, str(LAMBDA_DIR))

import lambda_function as ops  # noqa: E402


def _base_event(*, method: str, path: str, parameters: list | None = None, request_body: dict | None = None) -> dict:
    event = {
        "messageVersion": "1.0",
        "agent": {"name": "incidentiq-noc-agent", "id": "TESTAGENT", "alias": "live", "version": "DRAFT"},
        "actionGroup": "incidentiq-ops",
        "apiPath": path,
        "httpMethod": method,
        "parameters": parameters or [],
        "sessionAttributes": {},
        "promptSessionAttributes": {},
    }
    if request_body is not None:
        event["requestBody"] = request_body
    return event


def _body(resp: dict) -> dict:
    raw = resp["response"]["responseBody"]["application/json"]["body"]
    return json.loads(raw)


def test_environment_status_gib_degraded():
    event = _base_event(
        method="GET",
        path="/environments/{environment}/status",
        parameters=[{"name": "environment", "type": "string", "value": "GIB"}],
    )
    resp = ops.lambda_handler(event, None)
    assert resp["messageVersion"] == "1.0"
    assert resp["response"]["actionGroup"] == "incidentiq-ops"
    assert resp["response"]["httpStatusCode"] == 200
    data = _body(resp)
    assert data["status"] == "DEGRADED"
    assert data["active_alerts"] == 2


def test_environment_status_unknown_env():
    event = _base_event(
        method="GET",
        path="/environments/{environment}/status",
        parameters=[{"name": "environment", "type": "string", "value": "INVALID"}],
    )
    resp = ops.lambda_handler(event, None)
    assert resp["response"]["httpStatusCode"] == 400
    assert "error" in _body(resp)


def test_recent_alerts_gib():
    event = _base_event(
        method="GET",
        path="/environments/{environment}/alerts",
        parameters=[
            {"name": "environment", "type": "string", "value": "GIB"},
            {"name": "hours", "type": "integer", "value": "24"},
        ],
    )
    resp = ops.lambda_handler(event, None)
    assert resp["response"]["httpStatusCode"] == 200
    data = _body(resp)
    assert data["environment"] == "GIB"
    assert data["count"] == 2
    assert len(data["alerts"]) == 2


def test_create_incident_success():
    event = _base_event(
        method="POST",
        path="/incidents",
        request_body={
            "content": {
                "application/json": {
                    "properties": [
                        {"name": "title", "value": "Replication lag"},
                        {"name": "severity", "value": "P2"},
                        {"name": "environment", "value": "GIB"},
                    ]
                }
            }
        },
    )
    resp = ops.lambda_handler(event, None)
    assert resp["response"]["httpStatusCode"] == 200
    data = _body(resp)
    assert data["ticket_id"].startswith("INC-")
    assert data["status"] == "OPEN"
    assert data["severity"] == "P2"


def test_create_incident_missing_fields():
    event = _base_event(
        method="POST",
        path="/incidents",
        request_body={
            "content": {
                "application/json": {
                    "properties": [{"name": "title", "value": "Only title"}]
                }
            }
        },
    )
    resp = ops.lambda_handler(event, None)
    assert resp["response"]["httpStatusCode"] == 400
    assert "Missing required fields" in _body(resp)["error"]


def test_unknown_route_returns_404():
    event = _base_event(method="DELETE", path="/unknown")
    resp = ops.lambda_handler(event, None)
    assert resp["response"]["httpStatusCode"] == 404
