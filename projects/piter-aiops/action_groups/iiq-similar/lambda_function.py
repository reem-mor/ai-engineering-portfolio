"""Bedrock action group: find_similar_incidents."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

_ROOT = Path(__file__).resolve().parent
_DATA_DIR = _ROOT / "data"
_HISTORY = _DATA_DIR / "incident_history.csv"

from enrichment_tools import find_similar_incidents  # noqa: E402


def _params_to_dict(params: list) -> dict:
    return {p["name"]: p["value"] for p in (params or [])}


def _respond(event: dict, status: int, body: dict) -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "apiPath": event["apiPath"],
            "httpMethod": event["httpMethod"],
            "httpStatusCode": status,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
        "sessionAttributes": event.get("sessionAttributes", {}),
        "promptSessionAttributes": event.get("promptSessionAttributes", {}),
    }


def lambda_handler(event, context):
    logger.info("iiq-similar: %s", json.dumps(event))
    try:
        params = _params_to_dict(event.get("parameters", []))
        service = params.get("service", "")
        symptom = params.get("symptom", "")
        limit = int(params.get("limit", "5"))
        if not service or not symptom:
            return _respond(event, 400, {"error": "service and symptom required"})
        result = find_similar_incidents(
            service=service,
            symptom=symptom,
            limit=limit,
            history_path=_HISTORY,
        )
        return _respond(event, 200, result)
    except Exception as exc:
        logger.exception("iiq-similar failed")
        return _respond(event, 500, {"error": str(exc)})
