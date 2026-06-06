"""Boto3 SNS/SES dispatch with explicit live opt-in."""
from __future__ import annotations

import os

import boto3
from botocore.exceptions import ClientError


class NotificationDispatchError(Exception):
    """Raised when live notification dispatch is blocked or misconfigured."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def live_dispatch_enabled() -> bool:
    return os.environ.get("PITER_ENABLE_LIVE_DISPATCH", "false").lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def email_configured() -> bool:
    return bool(os.environ.get("PITER_SES_SENDER_EMAIL", "").strip())


def sms_configured() -> bool:
    """Direct SMS via SNS needs no topic ARN; topic path is optional."""
    return True


def allowlist_count() -> int:
    raw = os.environ.get("PITER_NOTIFICATION_ALLOWLIST", "")
    return len({item.strip() for item in raw.split(",") if item.strip()})


def dispatch_sms(phone: str, message: str) -> dict:
    topic_arn = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    region = os.environ.get("AWS_REGION", "us-east-1")
    sns = boto3.client("sns", region_name=region)
    if topic_arn:
        response = sns.publish(TopicArn=topic_arn, Message=message, Subject="PITER Escalation")
    else:
        response = sns.publish(PhoneNumber=phone, Message=message)
    return {"channel": "sms", "message_id": response.get("MessageId"), "sent": True}


def dispatch_email(to: str, subject: str, body: str) -> dict:
    sender = os.environ.get("PITER_SES_SENDER_EMAIL", "").strip()
    if not sender:
        raise NotificationDispatchError(
            "ses_not_configured",
            "PITER_SES_SENDER_EMAIL is not configured",
        )
    region = os.environ.get("AWS_REGION", "us-east-1")
    ses = boto3.client("ses", region_name=region)
    response = ses.send_email(
        Source=sender,
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
        },
    )
    return {"channel": "email", "message_id": response.get("MessageId"), "sent": True}


def dispatch_live(recipient: str, message: str, *, subject: str | None = None) -> dict:
    if not live_dispatch_enabled():
        raise NotificationDispatchError(
            "live_dispatch_disabled",
            "PITER_ENABLE_LIVE_DISPATCH is not true",
        )
    if recipient.startswith("+"):
        return dispatch_sms(recipient, message)
    if "@" in recipient:
        return dispatch_email(recipient, subject or "PITER escalation", message)
    raise NotificationDispatchError(
        "unknown_channel",
        "Recipient must be an E.164 phone (+...) or email address",
    )


def dispatch_live_safe(recipient: str, message: str, *, subject: str | None = None) -> dict:
    """Dispatch or raise NotificationDispatchError / ClientError."""
    try:
        return dispatch_live(recipient, message, subject=subject)
    except ClientError as exc:
        raise NotificationDispatchError(
            "aws_dispatch_failed",
            str(exc.response.get("Error", {}).get("Message", exc)),
        ) from exc
