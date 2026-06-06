"""Bedrock action group: correlate_deployments."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

_ROOT = Path(__file__).resolve().parent

from enrichment_tools import correlate_deployments  # noqa: E402

_DATA_DIR = _ROOT / "data"


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
    logger.info("iiq-correlate: %s", json.dumps(event))
    try:
        params = _params_to_dict(event.get("parameters", []))
        service = params.get("service", "")
        environment = params.get("environment", "")
        alert_time = params.get("alert_time", "")
        lookback = int(params.get("lookback_hours", "6"))
        if not service or not environment or not alert_time:
            return _respond(
                event,
                400,
                {"error": "service, environment, and alert_time are required"},
            )
        result = correlate_deployments(
            service=service,
            environment=environment,
            alert_time=alert_time,
            lookback_hours=lookback,
            data_dir=_DATA_DIR,
        )
        status = 400 if "error" in result else 200
        return _respond(event, status, result)
    except Exception as exc:
        logger.exception("iiq-correlate failed")
        return _respond(event, 500, {"error": str(exc)})
