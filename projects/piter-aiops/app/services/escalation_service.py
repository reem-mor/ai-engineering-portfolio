"""Invoke piter-escalation Lambda handler locally for Flask API routes."""
from __future__ import annotations

import importlib.util
import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LAMBDA_PATH = ROOT / "action_groups" / "piter-escalation" / "lambda_function.py"


@lru_cache(maxsize=1)
def _load_escalation_lambda():
    spec = importlib.util.spec_from_file_location("piter_escalation_lambda", LAMBDA_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load escalation lambda from {LAMBDA_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def mask_recipient(recipient: str) -> str:
    if not recipient:
        return ""
    if len(recipient) <= 4:
        return "*" * len(recipient)
    return f"{recipient[:2]}***{recipient[-2:]}"


def resolve_demo_recipient(channel: str) -> str:
    channel = channel.strip().lower()
    if channel == "sms":
        return os.environ.get("PITER_DEMO_SMS_RECIPIENT", "").strip()
    if channel == "email":
        return os.environ.get("PITER_DEMO_EMAIL_RECIPIENT", "").strip()
    raise ValueError(f"Unknown channel: {channel}")


def _build_event(operation: str, params: dict[str, str]) -> dict[str, Any]:
    items = [{"name": key, "type": "string", "value": value} for key, value in params.items()]
    if "operation" not in params:
        items.append({"name": "operation", "type": "string", "value": operation})
    return {
        "messageVersion": "1.0",
        "actionGroup": "piter-escalation",
        "apiPath": "/escalation",
        "httpMethod": "POST",
        "parameters": items,
        "sessionAttributes": {},
        "promptSessionAttributes": {},
    }


def invoke_escalation(operation: str, params: dict[str, str]) -> dict[str, Any]:
    mod = _load_escalation_lambda()
    response = mod.lambda_handler(_build_event(operation, params), None)
    raw = response["response"]["responseBody"]["application/json"]["body"]
    body = json.loads(raw)
    return {
        "http_status": int(response["response"]["httpStatusCode"]),
        **body,
    }


def notify_demo_channel(
    *,
    channel: str,
    incident_id: str,
    service: str,
    severity: str,
    confirmation_token: str,
    message: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    recipient = resolve_demo_recipient(channel)
    if not recipient:
        return {
            "http_status": 400,
            "ok": False,
            "error": f"PITER_DEMO_{channel.upper()}_RECIPIENT is not configured",
            "sent": False,
        }
    default_message = (
        f"PITER escalation: {severity} on {service} ({incident_id}). "
        "Review the incident in the PITER AiOps console."
    )
    params: dict[str, str] = {
        "operation": "live_notify",
        "service": service,
        "severity": severity,
        "incident_id": incident_id,
        "recipient": recipient,
        "message": message or default_message,
        "confirmation_token": confirmation_token,
    }
    if idempotency_key:
        params["idempotency_key"] = idempotency_key
    else:
        params["idempotency_key"] = f"{incident_id}:{channel}:{recipient}:{severity}"
    result = invoke_escalation("live_notify", params)
    result["recipient_configured"] = True
    result["channel"] = channel
    return result
