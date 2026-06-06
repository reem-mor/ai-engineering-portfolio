"""PITER Lambda: service ownership, on-call role, impact, priority, exposure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.enrichment_tools import lookup_owner, score_business_impact  # noqa: E402


def _params(event: dict) -> dict[str, str]:
    return {item["name"]: item["value"] for item in event.get("parameters", [])}


def _respond(event: dict, status: int, body: dict) -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "piter-service-context"),
            "apiPath": event.get("apiPath", "/service-context"),
            "httpMethod": event.get("httpMethod", "GET"),
            "httpStatusCode": status,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
        "sessionAttributes": event.get("sessionAttributes", {}),
        "promptSessionAttributes": event.get("promptSessionAttributes", {}),
    }


def lambda_handler(event, context):
    params = _params(event)
    path = event.get("apiPath", "/service-context")
    service = params.get("service", "")
    environment = params.get("environment", "")
    if not service or not environment:
        return _respond(event, 400, {"error": "service and environment are required"})
    if path == "/impact":
        severity = params.get("severity", "")
        if not severity:
            return _respond(event, 400, {"error": "severity is required"})
        result = score_business_impact(service=service, environment=environment, severity=severity)
    else:
        result = lookup_owner(service=service, environment=environment)
    return _respond(event, 400 if "error" in result else 200, result)
