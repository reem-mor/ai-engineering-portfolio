"""PITER Lambda: recent deployments, correlation, and rollback availability."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.enrichment_tools import correlate_deployments  # noqa: E402


def _params(event: dict) -> dict[str, str]:
    return {item["name"]: item["value"] for item in event.get("parameters", [])}


def _respond(event: dict, status: int, body: dict) -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "piter-recent-deployments"),
            "apiPath": event.get("apiPath", "/recent-deployments"),
            "httpMethod": event.get("httpMethod", "GET"),
            "httpStatusCode": status,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
        "sessionAttributes": event.get("sessionAttributes", {}),
        "promptSessionAttributes": event.get("promptSessionAttributes", {}),
    }


def lambda_handler(event, context):
    params = _params(event)
    service = params.get("service", "")
    environment = params.get("environment", "")
    alert_time = params.get("alert_time", "")
    if not all([service, environment, alert_time]):
        return _respond(event, 400, {"error": "service, environment, and alert_time are required"})
    result = correlate_deployments(
        service=service,
        environment=environment,
        alert_time=alert_time,
        lookback_hours=int(params.get("lookback_hours", "6")),
    )
    return _respond(event, 400 if "error" in result else 200, result)
