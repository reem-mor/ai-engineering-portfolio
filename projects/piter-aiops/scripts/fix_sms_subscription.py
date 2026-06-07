#!/usr/bin/env python3
"""Enable AWS End User Messaging SMS for PITER (console opt-in + auto-config).

AWS cannot subscribe an account to SMS via API alone — the first opt-in must happen
in the console. This script opens the right pages, polls until SMS APIs respond,
then sets spend limits and registers the sandbox destination phone.

Usage:
  python scripts/fix_sms_subscription.py
  python scripts/fix_sms_subscription.py --otp 123456
  python scripts/fix_sms_subscription.py --no-browser --wait-minutes 0
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

from app.services.notification_dispatch import (  # noqa: E402
    SMS_CONSOLE_URL,
    check_sms_account_ready,
)

BILLING_URL = "https://portal.aws.amazon.com/billing/signup?type=resubscribe#/resubscribed"
SNS_TEXT_URL = "https://us-east-1.console.aws.amazon.com/sns/v3/home?region=us-east-1#/mobile/text-messaging"


def _region() -> str:
    return os.environ.get("PITER_AWS_REGION", os.environ.get("AWS_REGION", "us-east-1")).strip()


def _phone() -> str:
    return os.environ.get("PITER_DEMO_SMS_RECIPIENT", "").strip()


def _open_console() -> None:
    for url in (SMS_CONSOLE_URL, SNS_TEXT_URL, BILLING_URL):
        webbrowser.open(url)


def _configure_sms(sns, *, monthly_limit: str) -> None:
    sns.set_sms_attributes(
        attributes={
            "MonthlySpendLimit": monthly_limit,
            "DefaultSMSType": "Transactional",
            "DeliveryStatusSuccessSamplingRate": "100",
        }
    )


def _sandbox_status(sns, phone: str) -> str:
    """Return verified | pending | missing."""
    try:
        resp = sns.list_sms_sandbox_phone_numbers()
    except ClientError:
        return "unknown"
    for item in resp.get("PhoneNumbers", []):
        if item.get("PhoneNumber") == phone:
            return "verified" if item.get("Status") == "Verified" else "pending"
    return "missing"


def _register_sandbox(sns, phone: str, otp: str | None) -> dict:
    status = _sandbox_status(sns, phone)
    if status == "verified":
        return {"status": "verified", "message": "Phone already verified in SMS sandbox."}

    if status == "missing":
        try:
            sns.create_sms_sandbox_phone_number(PhoneNumber=phone, LanguageCode="en-US")
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code not in {"UserError", "AuthorizationErrorException"}:
                if "already exists" not in str(exc).lower():
                    raise
        return {
            "status": "otp_sent",
            "message": f"Verification OTP sent to {phone}. Re-run with --otp <code>.",
        }

    if otp:
        sns.verify_sms_sandbox_phone_number(PhoneNumber=phone, OneTimePassword=otp)
        return {"status": "verified", "message": f"Verified {phone} in SMS sandbox."}

    return {
        "status": "otp_required",
        "message": f"OTP already sent to {phone}. Re-run: python scripts/fix_sms_subscription.py --otp <code>",
    }


def _send_test_sms(sns, phone: str) -> str | None:
    resp = sns.publish(
        PhoneNumber=phone,
        Message="PITER: AWS SMS is configured. Escalation alerts will reach this number.",
        MessageAttributes={
            "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
        },
    )
    return resp.get("MessageId")


def main() -> int:
    parser = argparse.ArgumentParser(description="Enable and configure AWS SMS for PITER")
    parser.add_argument("--monthly-limit", default="10", help="USD monthly SMS spend cap")
    parser.add_argument("--wait-minutes", type=int, default=15, help="Poll console opt-in (0=skip wait)")
    parser.add_argument("--poll-seconds", type=int, default=15, help="Poll interval")
    parser.add_argument("--otp", help="SMS sandbox verification code from your phone")
    parser.add_argument("--no-browser", action="store_true", help="Do not open AWS console tabs")
    parser.add_argument("--test-only", action="store_true", help="Only diagnose; do not configure")
    args = parser.parse_args()

    phone = _phone()
    region = _region()
    sns = boto3.client("sns", region_name=region)

    report: dict = {
        "phone": phone,
        "region": region,
        "sms_account": check_sms_account_ready(region=region),
        "steps": [],
    }

    if args.test_only:
        print(json.dumps(report, indent=2))
        return 0 if report["sms_account"].get("ready") else 1

    if not report["sms_account"].get("ready"):
        report["steps"].append("Console opt-in required (cannot be done via API).")
        print("\n=== AWS SMS not enabled yet ===\n")
        print("In the browser (logged in as admin-reem / profile reemmor):")
        print("  1. Billing resubscribe — confirm account / payment if prompted")
        print("  2. End User Messaging SMS — accept terms on the Overview page")
        print("  3. Text messaging preferences — set monthly spend limit (e.g. $10)")
        print(f"  4. SMS sandbox — add and verify {phone}\n")
        print(f"  Billing:  {BILLING_URL}")
        print(f"  SMS:      {SMS_CONSOLE_URL}\n")

        if not args.no_browser:
            _open_console()

        if args.wait_minutes > 0:
            deadline = time.time() + args.wait_minutes * 60
            while time.time() < deadline:
                status = check_sms_account_ready(region=region)
                if status.get("ready"):
                    report["sms_account"] = status
                    print("\nSMS service detected — continuing setup.\n")
                    break
                print(f"[{time.strftime('%H:%M:%S')}] Waiting for console opt-in...")
                time.sleep(args.poll_seconds)
            else:
                report["steps"].append("Timed out waiting for console opt-in.")
                print(json.dumps(report, indent=2))
                print("\nFinish the console steps above, then re-run this script.\n")
                return 1

    if not check_sms_account_ready(region=region).get("ready"):
        print(json.dumps(report, indent=2))
        return 1

    try:
        _configure_sms(sns, monthly_limit=args.monthly_limit)
        report["steps"].append(f"Set MonthlySpendLimit=${args.monthly_limit}, DefaultSMSType=Transactional")
    except ClientError as exc:
        report["steps"].append(f"WARN set_sms_attributes: {exc.response.get('Error', {}).get('Message', exc)}")

    sandbox = _register_sandbox(sns, phone, args.otp)
    report["sandbox"] = sandbox
    report["steps"].append(sandbox["message"])

    if sandbox["status"] in {"otp_sent", "otp_required"}:
        print(json.dumps(report, indent=2))
        print(f"\nEnter the OTP from {phone}, then run:")
        print(f"  python scripts/fix_sms_subscription.py --otp <code> --no-browser --wait-minutes 0\n")
        return 1

    if sandbox["status"] == "verified":
        try:
            mid = _send_test_sms(sns, phone)
            report["test_message_id"] = mid
            report["steps"].append(f"Test SMS published (MessageId={mid})")
        except ClientError as exc:
            report["steps"].append(f"Test SMS failed: {exc.response.get('Error', {}).get('Message', exc)}")

    report["sms_account"] = check_sms_account_ready(region=region)
    print(json.dumps(report, indent=2))

    if report["sms_account"].get("ready") and sandbox["status"] == "verified":
        print("\nRun full app test: python scripts/test_live_notify.py\n")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
