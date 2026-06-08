#!/usr/bin/env python3
"""Diagnose why live SMS may not reach a phone."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

from app.services.notification_dispatch import (  # noqa: E402
    SMS_BILLING_RESUBSCRIBE_URL,
    SMS_CONSOLE_URL,
    _check_sms_topic_route,
    check_sms_account_ready,
    sms_preflight_enabled,
    sms_use_topic,
    sms_use_voice_v2,
)


def _region() -> str:
    return os.environ.get("PITER_AWS_REGION", os.environ.get("AWS_REGION", "us-east-1")).strip()


def _session():
    profile = os.environ.get("AWS_PROFILE", "").strip() or None
    return boto3.Session(profile_name=profile, region_name=_region())


def _sns():
    return _session().client("sns")


def _voice_v2():
    return _session().client("pinpoint-sms-voice-v2")


def _sandbox_status(sns, phone: str) -> str:
    try:
        resp = sns.list_sms_sandbox_phone_numbers()
    except ClientError:
        return "unknown"
    for item in resp.get("PhoneNumbers", []):
        if item.get("PhoneNumber") == phone:
            return str(item.get("Status") or "unknown").lower()
    return "not_in_sandbox"


def _opted_out(sns, phone: str) -> bool | None:
    try:
        return bool(sns.check_if_phone_number_is_opted_out(phoneNumber=phone).get("isOptedOut"))
    except ClientError:
        return None


def _sms_attributes(sns) -> dict:
    try:
        return sns.get_sms_attributes().get("attributes", {})
    except ClientError as exc:
        return {"error": str(exc)}


def _account_tier() -> str:
    try:
        attrs = _voice_v2().describe_account_attributes().get("AccountAttributes", [])
        return str(next((a.get("Value") for a in attrs if a.get("Name") == "ACCOUNT_TIER"), "UNKNOWN"))
    except ClientError:
        return "unknown"


def _topic_delivery_hint() -> dict:
    topic = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    if not topic:
        return {"available": False}
    try:
        cw = _session().client("cloudwatch")
        from datetime import datetime, timedelta, timezone

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)
        resp = cw.get_metric_statistics(
            Namespace="AWS/SNS",
            MetricName="NumberOfNotificationsDelivered",
            Dimensions=[{"Name": "TopicName", "Value": "piter-aiops-escalation"}],
            StartTime=start,
            EndTime=end,
            Period=86400,
            Statistics=["Sum"],
        )
        total = sum(float(p.get("Sum", 0)) for p in resp.get("Datapoints", []))
        return {"available": True, "topic_delivered_last_7d": int(total)}
    except ClientError as exc:
        return {"available": True, "cloudwatch_error": str(exc)}


def main() -> int:
    phone = os.environ.get("PITER_DEMO_SMS_RECIPIENT", "").strip()
    sns = _sns()
    status = check_sms_account_ready(phone=phone or None)
    attrs = _sms_attributes(sns)
    spend = str(attrs.get("MonthlySpendLimit", "")).strip()
    topic_route = _check_sms_topic_route(phone=phone) if phone else {"ready": False}
    use_voice = sms_use_voice_v2()

    report: dict = {
        "demo_phone": phone,
        "preflight_enabled": sms_preflight_enabled(),
        "sms_use_voice_v2": use_voice,
        "sms_use_topic_env": sms_use_topic(),
        "account_tier": _account_tier(),
        "sms_account": status,
        "sms_attributes": attrs,
        "sandbox_status": _sandbox_status(sns, phone) if phone else "no_phone",
        "opted_out": _opted_out(sns, phone) if phone else None,
        "topic_route": topic_route,
        "topic_delivery_hint": _topic_delivery_hint(),
        "console_url": SMS_CONSOLE_URL,
        "billing_url": SMS_BILLING_RESUBSCRIBE_URL,
        "fix_script": "python scripts/fix_sms_subscription.py",
        "next_steps": [],
        "likely_causes": [],
    }

    if spend == "1":
        report["likely_causes"].append(
            "MonthlySpendLimit is $1. International SMS to +972 often costs $0.08–0.15 each; "
            "AWS may accept the API call (MessageId) but stop delivering after the cap. "
            "Request a higher SMS spend limit via AWS Support (console may block raises above $1)."
        )

    if sms_use_topic() and use_voice:
        report["likely_causes"].append(
            "PITER_SNS_SMS_USE_TOPIC=true is legacy fan-out. Prefer PITER_SMS_USE_VOICE_V2=true "
            "and PITER_SNS_SMS_USE_TOPIC=false for sandbox Israel numbers."
        )

    if report["sandbox_status"] != "verified":
        report["likely_causes"].append(
            f"Phone sandbox status is '{report['sandbox_status']}' — run: "
            "python scripts/fix_sms_subscription.py"
        )

    if report.get("opted_out") is True:
        report["likely_causes"].append("Phone is opted out of AWS SMS — opt back in via SNS console.")

    if status.get("ready") and report["sandbox_status"] == "verified" and not report.get("opted_out"):
        report["next_steps"] = [
            "Ensure PITER_SMS_USE_VOICE_V2=true and PITER_SNS_SMS_USE_TOPIC=false in .env.",
            "Re-run: python scripts/test_live_notify.py",
            "Check phone within 2–3 minutes; sandbox messages may show sender NOTICE.",
            f"If still nothing: {SMS_CONSOLE_URL} → Text messaging → Delivery status logs.",
            "Open AWS Support case to raise MonthlySpendLimit above $1 for Israel SMS.",
        ]
    else:
        report["next_steps"] = [
            "Run: python scripts/fix_sms_subscription.py",
            f"Or manually: {SMS_CONSOLE_URL}",
            "Accept SMS terms, verify sandbox phone, set Transactional type.",
            f"Account verification if prompted: {SMS_BILLING_RESUBSCRIBE_URL}",
        ]

    print(json.dumps(report, indent=2))
    ok = (
        status.get("ready")
        and report["sandbox_status"] == "verified"
        and report.get("opted_out") is not True
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
