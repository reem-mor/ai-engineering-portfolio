"""
IncidentIQ — Bedrock Agent action group Lambda.

One Lambda hosts multiple operations. Bedrock routes each call to us with
`apiPath` + `httpMethod`; we route internally and return a strict response
envelope that Bedrock requires.

Operations:
  GET  /environments/{environment}/status          - read
  GET  /environments/{environment}/alerts?hours=N  - read
  POST /incidents                                  - WRITE (agent should confirm first)
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


# ---------------------------------------------------------------------------
# Mock backend (replace with real calls when you wire to prod systems)
# ---------------------------------------------------------------------------

VALID_ENVIRONMENTS = {"NJ", "DGE", "GIB", "GBGA", "UKGC", "MGM", "MIRAGE"}

MOCK_STATUSES = {
    "NJ": {"status": "HEALTHY", "active_alerts": 0, "last_check": "2026-06-03T10:14:00Z"},
    "GIB": {"status": "DEGRADED", "active_alerts": 2, "last_check": "2026-06-03T10:13:50Z"},
    "MGM": {"status": "HEALTHY", "active_alerts": 0, "last_check": "2026-06-03T10:14:01Z"},
    "MIRAGE": {"status": "HEALTHY", "active_alerts": 0, "last_check": "2026-06-03T10:14:00Z"},
}

MOCK_ALERTS = {
    "GIB": [
        {
            "alert_id": "ALT-1023",
            "severity": "P2",
            "title": "DB replication lag > 30s",
            "fired_at": "2026-06-03T09:42:11Z",
            "host": "gib-db-replica-02",
        },
        {
            "alert_id": "ALT-1025",
            "severity": "P3",
            "title": "Disk usage 85% on /var/log",
            "fired_at": "2026-06-03T09:55:33Z",
            "host": "gib-app-04",
        },
    ],
}


# ---------------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------------

def get_environment_status(env: str) -> dict:
    env = env.upper()
    if env not in VALID_ENVIRONMENTS:
        return {
            "error": f"Unknown environment '{env}'.",
            "valid_environments": sorted(VALID_ENVIRONMENTS),
        }
    return MOCK_STATUSES.get(env, {"status": "UNKNOWN", "active_alerts": 0})


def get_recent_alerts(env: str, hours: int) -> dict:
    env = env.upper()
    if env not in VALID_ENVIRONMENTS:
        return {"error": f"Unknown environment '{env}'."}
    if not 1 <= hours <= 168:
        return {"error": "hours must be between 1 and 168."}

    alerts = MOCK_ALERTS.get(env, [])
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent = [
        a
        for a in alerts
        if datetime.fromisoformat(a["fired_at"].replace("Z", "+00:00")) >= cutoff
    ]
    return {"environment": env, "window_hours": hours, "count": len(recent), "alerts": recent}


def create_incident(payload: dict) -> dict:
    required = {"title", "severity", "environment"}
    missing = required - payload.keys()
    if missing:
        return {"error": f"Missing required fields: {sorted(missing)}"}

    env = str(payload["environment"]).upper()
    if env not in VALID_ENVIRONMENTS:
        return {"error": f"Unknown environment '{env}'."}
    if payload["severity"] not in {"P1", "P2", "P3", "P4"}:
        return {"error": "severity must be one of P1, P2, P3, P4."}

    ticket_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    return {
        "ticket_id": ticket_id,
        "status": "OPEN",
        "title": payload["title"],
        "severity": payload["severity"],
        "environment": env,
        "description": payload.get("description", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Bedrock Agent contract helpers
# ---------------------------------------------------------------------------

def _params_to_dict(params: list) -> dict:
    """Bedrock sends path/query params as a list of {name, type, value} objects."""
    return {p["name"]: p["value"] for p in (params or [])}


def _request_body_to_dict(request_body: dict) -> dict:
    """Bedrock wraps JSON request bodies in a nested 'properties' list."""
    if not request_body:
        return {}
    props = (
        request_body.get("content", {})
        .get("application/json", {})
        .get("properties", [])
    )
    return {p["name"]: p["value"] for p in props}


def _respond(event: dict, status: int, body: dict) -> dict:
    """Build the exact response shape Bedrock Agents require."""
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event["actionGroup"],
            "apiPath": event["apiPath"],
            "httpMethod": event["httpMethod"],
            "httpStatusCode": status,
            "responseBody": {
                "application/json": {"body": json.dumps(body)}
            },
        },
        "sessionAttributes": event.get("sessionAttributes", {}),
        "promptSessionAttributes": event.get("promptSessionAttributes", {}),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    logger.info("Bedrock action invoked: %s", json.dumps(event))

    try:
        api_path = event["apiPath"]
        http_method = event["httpMethod"]
        params = _params_to_dict(event.get("parameters", []))

        if http_method == "GET" and api_path == "/environments/{environment}/status":
            result = get_environment_status(params.get("environment", ""))

        elif http_method == "GET" and api_path == "/environments/{environment}/alerts":
            hours = int(params.get("hours", 24))
            result = get_recent_alerts(params.get("environment", ""), hours)

        elif http_method == "POST" and api_path == "/incidents":
            body = _request_body_to_dict(event.get("requestBody", {}))
            result = create_incident(body)

        else:
            return _respond(event, 404, {"error": f"No handler for {http_method} {api_path}"})

        status = 400 if "error" in result else 200
        return _respond(event, status, result)

    except Exception as exc:
        logger.exception("Unhandled error in action group")
        return _respond(event, 500, {"error": "Internal error", "detail": str(exc)})
