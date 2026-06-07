#!/usr/bin/env python3
"""Provision SNS + SES resources for PITER live escalation (idempotent).

Creates:
  - SNS topic: piter-aiops-escalation (tagged, SSE optional via account default)
  - SES configuration set: piter-aiops-escalations (CloudWatch event metrics)
  - SES verified email identities (sender + optional recipients for sandbox)
  - IAM managed policy: PITER-AiOps-Notifications (least privilege)
  - SNS SMS safety defaults (transactional type hint via app; spend limit here)

Usage:
  cd projects/piter-aiops
  python scripts/setup_notifications.py --sender-email you@example.com
  python scripts/setup_notifications.py --sender-email you@example.com \\
      --verify-recipients teacher@school.edu --dry-run

Requires AWS credentials (AWS_PROFILE or default chain) in us-east-1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

import boto3  # noqa: E402
from botocore.exceptions import ClientError  # noqa: E402

TOPIC_NAME = "piter-aiops-escalation"
CONFIG_SET_NAME = "piter-aiops-escalations"
POLICY_NAME = "PITER-AiOps-Notifications"
TAGS = [
    {"Key": "Project", "Value": "piter-aiops"},
    {"Key": "Component", "Value": "escalation-notifications"},
    {"Key": "ManagedBy", "Value": "setup_notifications.py"},
]


def _session(region: str, profile: str | None) -> boto3.Session:
    kwargs: dict = {"region_name": region}
    if profile:
        kwargs["profile_name"] = profile
    return boto3.Session(**kwargs)


def _ensure_sns_topic(sns, *, dry_run: bool) -> str:
    if dry_run:
        return f"arn:aws:sns:us-east-1:000000000000:{TOPIC_NAME}"
    try:
        resp = sns.create_topic(
            Name=TOPIC_NAME,
            Tags=[{"Key": t["Key"], "Value": t["Value"]} for t in TAGS],
        )
        arn = resp["TopicArn"]
        print(f"  SNS topic: {arn}")
        return arn
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "InvalidParameter":
            raise
        resp = sns.create_topic(Name=TOPIC_NAME)
        arn = resp["TopicArn"]
        sns.tag_resource(ResourceArn=arn, Tags=TAGS)
        print(f"  SNS topic (existing): {arn}")
        return arn


def _configure_sns_sms(sns, *, monthly_limit: str, dry_run: bool) -> None:
    if dry_run:
        print(f"  SNS SMS monthly spend limit: ${monthly_limit}")
        return
    console = "https://us-east-1.console.aws.amazon.com/sms-voice/home?region=us-east-1#/overview"
    try:
        sns.set_sms_attributes(
            attributes={
                "MonthlySpendLimit": monthly_limit,
                "DefaultSMSType": "Transactional",
                "DeliveryStatusSuccessSamplingRate": "100",
            }
        )
        print(f"  SNS SMS: MonthlySpendLimit=${monthly_limit}, DefaultSMSType=Transactional")
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        message = exc.response.get("Error", {}).get("Message", "")
        print(f"  WARN: SNS SMS preferences skipped ({code}).")
        if "PinpointSmsVoiceV2" in message:
            print("  AWS End User Messaging SMS is not enabled yet.")
            print(f"  1. Open {console}")
            print("  2. Accept SMS terms and set a monthly spend limit.")
            print("  3. Re-run this script, then: python scripts/diagnose_sms.py")
        else:
            print(
                "  Enable SMS in the End User Messaging console if you need live SMS."
            )


def _ensure_ses_configuration_set(sesv2, *, dry_run: bool) -> None:
    if dry_run:
        print(f"  SES configuration set: {CONFIG_SET_NAME}")
        return
    try:
        sesv2.create_configuration_set(ConfigurationSetName=CONFIG_SET_NAME)
        print(f"  Created SES configuration set: {CONFIG_SET_NAME}")
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "AlreadyExistsException":
            raise
        print(f"  SES configuration set exists: {CONFIG_SET_NAME}")

    try:
        sesv2.create_configuration_set_event_destination(
            ConfigurationSetName=CONFIG_SET_NAME,
            EventDestinationName="cloudwatch-metrics",
            EventDestination={
                "Enabled": True,
                "MatchingEventTypes": ["SEND", "DELIVERY", "BOUNCE", "COMPLAINT", "REJECT"],
                "CloudWatchDestination": {
                    "DimensionConfigurations": [
                        {
                            "DimensionName": "piter-escalation",
                            "DimensionValueSource": "MESSAGE_TAG",
                            "DefaultDimensionValue": "escalation",
                        }
                    ]
                },
            },
        )
        print("  SES event destination: CloudWatch (send/bounce/complaint metrics)")
    except ClientError as exc:
        if exc.response["Error"]["Code"] not in {
            "AlreadyExistsException",
            "EventDestinationAlreadyExistsException",
        }:
            raise
        print("  SES CloudWatch event destination already configured")


def _ensure_email_identity(sesv2, email: str, *, dry_run: bool) -> str:
    if dry_run:
        print(f"  SES identity (dry-run): {email}")
        return "Pending"
    try:
        sesv2.create_email_identity(
            EmailIdentity=email,
            Tags=[{"Key": t["Key"], "Value": t["Value"]} for t in TAGS],
        )
        print(f"  SES identity created - check inbox to verify: {email}")
        return "Pending"
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "AlreadyExistsException":
            raise
    detail = sesv2.get_email_identity(EmailIdentity=email)
    status = detail.get("VerifiedForSendingStatus", False)
    label = "Success" if status else "Pending"
    print(f"  SES identity {email}: {'Verified' if status else 'Pending verification'}")
    return label


def _render_policy(*, region: str, account: str, sender: str, recipients: list[str]) -> str:
    template = (ROOT / "infra" / "notifications_policy.json").read_text(encoding="utf-8")
    recipient = recipients[0] if recipients else sender
    return (
        template.replace("REGION", region)
        .replace("ACCOUNT_ID", account)
        .replace("SENDER_EMAIL", sender)
        .replace("RECIPIENT_EMAIL", recipient)
    )


def _attach_managed_policy(
    iam,
    policy_arn: str,
    *,
    iam_user: str | None,
    role_names: list[str],
    dry_run: bool,
) -> None:
    if iam_user:
        if dry_run:
            print(f"  Attach {policy_arn} -> user/{iam_user}")
        else:
            try:
                iam.attach_user_policy(UserName=iam_user, PolicyArn=policy_arn)
                print(f"  Attached to IAM user: {iam_user}")
            except ClientError as exc:
                if exc.response["Error"]["Code"] == "EntityAlreadyExists":
                    print(f"  IAM user already has policy: {iam_user}")
                elif exc.response["Error"]["Code"] == "LimitExceeded":
                    print(f"  IAM user {iam_user} at managed policy limit — detach unused policies or use a group")
                else:
                    raise
    for role_name in role_names:
        role_name = role_name.strip()
        if not role_name:
            continue
        if dry_run:
            print(f"  Attach {policy_arn} -> role/{role_name}")
            continue
        try:
            iam.get_role(RoleName=role_name)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchEntity":
                print(f"  SKIP role (not found): {role_name}")
                continue
            raise
        try:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            print(f"  Attached to IAM role: {role_name}")
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "EntityAlreadyExists":
                print(f"  Role already has policy: {role_name}")
            else:
                raise


def _ensure_iam_policy(iam, policy_doc: str, *, account: str, dry_run: bool) -> str:
    if dry_run:
        print(f"  IAM policy (dry-run): {POLICY_NAME}")
        return f"arn:aws:iam::{account}:policy/{POLICY_NAME}"
    try:
        resp = iam.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=policy_doc,
            Description="PITER AiOps SNS/SES escalation - least privilege",
            Tags=[{"Key": t["Key"], "Value": t["Value"]} for t in TAGS],
        )
        arn = resp["Policy"]["Arn"]
        print(f"  Created IAM policy: {arn}")
        return arn
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "EntityAlreadyExists":
            raise
        arn = f"arn:aws:iam::{account}:policy/{POLICY_NAME}"
        iam.create_policy_version(
            PolicyArn=arn,
            PolicyDocument=policy_doc,
            SetAsDefault=True,
        )
        print(f"  Updated IAM policy: {arn}")
        return arn


def _print_account_status(sesv2) -> None:
    account = sesv2.get_account()
    sandbox = not account.get("ProductionAccessEnabled", False)
    print("\n--- SES account ---")
    print(f"  Production access: {'yes' if not sandbox else 'no (SANDBOX)'}")
    if sandbox:
        print("  Sandbox rule: verify BOTH sender and every recipient email in SES.")
    quota = account.get("SendQuota", {})
    print(f"  24h send quota: {quota.get('Max24HourSend', '?')} (sent: {quota.get('SentLast24Hours', 0)})")


def _print_env_snippet(*, topic_arn: str, sender: str) -> None:
    print("\n--- Add to projects/piter-aiops/.env (do not commit secrets) ---")
    print(f"PITER_SES_SENDER_EMAIL={sender}")
    print(f"PITER_SES_CONFIGURATION_SET={CONFIG_SET_NAME}")
    print(f"PITER_SNS_TOPIC_ARN={topic_arn}")
    print("# Optional - leave empty to use direct SNS SMS publish to phone:")
    print("# PITER_SNS_TOPIC_ARN=")
    print("PITER_DEMO_EMAIL_RECIPIENT=<recipient-from-allowlist>")
    print("PITER_DEMO_SMS_RECIPIENT=<your-e164-phone>")


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision PITER SNS/SES notification resources")
    parser.add_argument("--sender-email", required=True, help="Verified SES From address")
    parser.add_argument(
        "--verify-recipients",
        nargs="*",
        default=[],
        help="Additional emails to verify (required in SES sandbox)",
    )
    parser.add_argument("--region", default="", help="AWS region (default: PITER_AWS_REGION or us-east-1)")
    parser.add_argument("--profile", default="", help="AWS profile (default: AWS_PROFILE from .env)")
    parser.add_argument("--sms-monthly-limit", default="1", help="SNS SMS monthly spend cap (USD)")
    parser.add_argument("--skip-iam", action="store_true", help="Skip IAM managed policy creation")
    parser.add_argument(
        "--iam-user",
        default=os.environ.get("PITER_IAM_USER", "admin-reem"),
        help="Attach managed policy to this IAM user (default: admin-reem)",
    )
    parser.add_argument(
        "--attach-roles",
        nargs="*",
        default=["IncidentRagBedrockEC2Role", "incidentiq-lambda-role"],
        help="IAM roles to attach managed policy (EC2/Lambda runtime)",
    )
    parser.add_argument("--skip-attach", action="store_true", help="Create/update policy only; do not attach")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    region = args.region or os.environ.get("PITER_AWS_REGION", "us-east-1")
    profile = args.profile or os.environ.get("AWS_PROFILE") or None
    sender = args.sender_email.strip().lower()
    if not sender or "@" not in sender:
        print("Invalid --sender-email", file=sys.stderr)
        return 1

    session = _session(region, profile)
    sts = session.client("sts")
    account = sts.get_caller_identity()["Account"]
    sns = session.client("sns")
    sesv2 = session.client("sesv2")
    iam = session.client("iam")

    print(f"Account {account}  Region {region}  Profile {profile or '(default)'}")
    if args.dry_run:
        print("DRY RUN - no AWS changes\n")

    print("\n=== SNS ===")
    topic_arn = _ensure_sns_topic(sns, dry_run=args.dry_run)
    _configure_sns_sms(sns, monthly_limit=args.sms_monthly_limit, dry_run=args.dry_run)

    print("\n=== SES ===")
    _ensure_ses_configuration_set(sesv2, dry_run=args.dry_run)
    _ensure_email_identity(sesv2, sender, dry_run=args.dry_run)
    for email in args.verify_recipients:
        em = email.strip().lower()
        if em and em != sender and "@" in em:
            _ensure_email_identity(sesv2, em, dry_run=args.dry_run)

    if not args.dry_run:
        _print_account_status(sesv2)

    recipient_emails = [
        email.strip().lower()
        for email in args.verify_recipients
        if email.strip() and "@" in email
    ]
    if not recipient_emails:
        recipient_emails = [sender]

    print("\n=== IAM ===")
    policy_doc = _render_policy(
        region=region,
        account=account,
        sender=sender,
        recipients=recipient_emails,
    )
    resolved_path = ROOT / "infra" / "notifications_policy_resolved.json"
    if not args.dry_run:
        resolved_path.write_text(json.dumps(json.loads(policy_doc), indent=2) + "\n", encoding="utf-8")
        print(f"  Wrote {resolved_path.relative_to(ROOT)}")
    if not args.skip_iam:
        policy_arn = _ensure_iam_policy(iam, policy_doc, account=account, dry_run=args.dry_run)
        if not args.skip_attach:
            _attach_managed_policy(
                iam,
                policy_arn,
                iam_user=(args.iam_user.strip() or None),
                role_names=args.attach_roles,
                dry_run=args.dry_run,
            )
        else:
            print(f"  Manual attach: aws iam attach-user-policy --user-name {args.iam_user} --policy-arn {policy_arn}")

    _print_env_snippet(topic_arn=topic_arn, sender=sender)

    print("\nNext steps:")
    print("  1. Click verification links AWS emailed for each identity (sandbox: all recipients too).")
    print("  2. Update .env with the snippet above (no angle brackets on email addresses).")
    print("  3. Restart Flask and check Settings for notification readiness.")
    print("  4. For production email to anyone: SES console - Request production access.")
    print("  5. For SMS: enable End User Messaging, verify sandbox phone, run scripts/diagnose_sms.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
