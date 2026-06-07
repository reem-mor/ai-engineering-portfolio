"""Bedrock action group: lookup_owner + score_business_impact."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

_ROOT = Path(__file__).resolve().parent
_DATA_DIR = _ROOT / "data"

from enrichment_tools import lookup_owner, score_business_impact  # noqa: E402


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
    logger.info("iiq-context: %s %s", event.get("apiPath"), event.get("httpMethod"))
    try:
        params = _params_to_dict(event.get("parameters", []))
        path = event["apiPath"]
        if path == "/owner":
            service = params.get("service", "")
            environment = params.get("environment", "")
            if not service or not environment:
                return _respond(event, 400, {"error": "service and environment required"})
            result = lookup_owner(service=service, environment=environment, data_dir=_DATA_DIR)
        elif path == "/impact":
            service = params.get("service", "")
            environment = params.get("environment", "")
            severity = params.get("severity", "")
            if not all([service, environment, severity]):
                return _respond(event, 400, {"error": "service, environment, severity required"})
            result = score_business_impact(
                service=service,
                environment=environment,
                severity=severity,
                data_dir=_DATA_DIR,
            )
        else:
            return _respond(event, 404, {"error": f"Unknown path {path}"})
        status = 400 if "error" in result else 200
        return _respond(event, status, result)
    except Exception as exc:
        logger.exception("iiq-context failed")
        return _respond(event, 500, {"error": str(exc)})
