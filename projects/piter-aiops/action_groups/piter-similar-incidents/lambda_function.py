"""PITER Lambda: historical incident matching, root cause, resolution, MTTR."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.enrichment_tools import find_similar_incidents  # noqa: E402


def _params(event: dict) -> dict[str, str]:
    return {item["name"]: item["value"] for item in event.get("parameters", [])}


def _respond(event: dict, status: int, body: dict) -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "piter-similar-incidents"),
            "apiPath": event.get("apiPath", "/similar-incidents"),
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
    symptom = params.get("symptom", "")
    if not service or not symptom:
        return _respond(event, 400, {"error": "service and symptom are required"})
    result = find_similar_incidents(
        service=service,
        symptom=symptom,
        limit=int(params.get("limit", "5")),
    )
    return _respond(event, 400 if "error" in result else 200, result)
