"""PITER Lambda: escalation preview and safe notification flow."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SENT_IDEMPOTENCY_KEYS: set[str] = set()


def _ensure_app_import_path() -> None:
    root = Path(__file__).resolve().parents[2]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def _params(event: dict) -> dict[str, str]:
    params = {item["name"]: item["value"] for item in event.get("parameters", [])}
    content = event.get("requestBody", {}).get("content", {})
    props = content.get("application/json", {}).get("properties", [])
    params.update({item["name"]: item["value"] for item in props})
    return params


def _respond(event: dict, status: int, body: dict) -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", "piter-escalation"),
            "apiPath": event.get("apiPath", "/escalation"),
            "httpMethod": event.get("httpMethod", "POST"),
            "httpStatusCode": status,
            "responseBody": {"application/json": {"body": json.dumps(body)}},
        },
        "sessionAttributes": event.get("sessionAttributes", {}),
        "promptSessionAttributes": event.get("promptSessionAttributes", {}),
    }


def _csv_env(name: str, default: str = "") -> set[str]:
    raw = os.environ.get(name, default)
    return {item.strip() for item in raw.split(",") if item.strip()}


def _mask_recipient(recipient: str) -> str:
    if not recipient:
        return ""
    if len(recipient) <= 4:
        return "*" * len(recipient)
    return f"{recipient[:2]}***{recipient[-2:]}"


def _live_dispatch_enabled() -> bool:
    return os.environ.get("PITER_ENABLE_LIVE_DISPATCH", "false").lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def _email_configured() -> bool:
    return bool(os.environ.get("PITER_SES_SENDER_EMAIL", "").strip())


def _policy_preview(service: str, severity: str, recipient: str) -> dict:
    return {
        "service": service,
        "severity": severity,
        "policy": "piter-standard-escalation",
        "recipient": _mask_recipient(recipient),
        "channels": ["sns", "ses"],
        "live_dispatch_allowed": _live_dispatch_enabled(),
    }


def _live_block_reasons(params: dict[str, str], key: str) -> list[str]:
    reasons = []
    severity = params.get("severity", "")
    recipient = params.get("recipient", "")
    if os.environ.get("PITER_NOTIFICATION_MODE", "mock") != "live":
        reasons.append("PITER_NOTIFICATION_MODE is not live")
    if not _live_dispatch_enabled():
        reasons.append("PITER_ENABLE_LIVE_DISPATCH is not true")
    if os.environ.get("PITER_NOTIFICATION_REQUIRE_CONFIRMATION", "false").lower() != "true":
        reasons.append("confirmation requirement is not enabled")
    if params.get("confirmation_token", "") != os.environ.get("PITER_NOTIFICATION_CONFIRMATION_TOKEN", ""):
        reasons.append("confirmation token is invalid")
    if recipient not in _csv_env("PITER_NOTIFICATION_ALLOWLIST"):
        reasons.append("recipient is not allowlisted")
    if severity not in _csv_env("PITER_NOTIFICATION_ALLOWED_SEVERITIES", "P1,P2"):
        reasons.append("incident severity is not allowed")
    if "@" in recipient and not _email_configured():
        reasons.append("PITER_SES_SENDER_EMAIL is not configured")
    if key in SENT_IDEMPOTENCY_KEYS:
        reasons.append("message was already sent")
    return reasons


def lambda_handler(event, context):
    params = _params(event)
    operation = params.get("operation", "preview")
    service = params.get("service", "")
    severity = params.get("severity", "")
    incident_id = params.get("incident_id", "")
    recipient = params.get("recipient", "")
    message = params.get("message", "")
    key = params.get("idempotency_key") or f"{incident_id}:{recipient}:{severity}"

    if operation not in {"preview", "mock_notify", "live_notify"}:
        return _respond(event, 404, {"error": f"Unknown operation {operation}"})
    if not all([service, severity, incident_id]):
        return _respond(event, 400, {"error": "service, severity, and incident_id are required"})

    preview = _policy_preview(service, severity, recipient)
    if operation == "preview":
        return _respond(event, 200, {"mode": "preview", "escalation": preview})
    if not recipient or not message:
        return _respond(event, 400, {"error": "recipient and message are required for notification"})

    if operation == "mock_notify":
        return _respond(
            event,
            200,
            {
                "mode": "mock",
                "sent": False,
                "recipient": _mask_recipient(recipient),
                "message_preview": message[:160],
                "idempotency_key": key,
            },
        )

    block_reasons = _live_block_reasons(params, key)
    if block_reasons:
        return _respond(
            event,
            403,
            {
                "mode": os.environ.get("PITER_NOTIFICATION_MODE", "mock"),
                "sent": False,
                "blocked": True,
                "reasons": block_reasons,
                "recipient": _mask_recipient(recipient),
            },
        )

    _ensure_app_import_path()
    from app.services.notification_dispatch import NotificationDispatchError, dispatch_live_safe

    subject = f"[PITER {severity}] {incident_id} — {service}"
    try:
        dispatch_result = dispatch_live_safe(
            recipient,
            message,
            subject=subject,
            incident_id=incident_id,
        )
    except NotificationDispatchError as exc:
        return _respond(
            event,
            403,
            {
                "mode": "live",
                "sent": False,
                "blocked": True,
                "reasons": [exc.message],
                "recipient": _mask_recipient(recipient),
            },
        )

    SENT_IDEMPOTENCY_KEYS.add(key)
    return _respond(
        event,
        200,
        {
            "mode": "live",
            "sent": True,
            "channel": dispatch_result["channel"],
            "message_id": dispatch_result.get("message_id"),
            "recipient": _mask_recipient(recipient),
            "idempotency_key": key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
