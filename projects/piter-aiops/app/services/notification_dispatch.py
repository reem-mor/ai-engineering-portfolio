"""Boto3 SNS/SES dispatch with explicit live opt-in."""
from __future__ import annotations

import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


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


def _aws_region() -> str:
    return os.environ.get("PITER_AWS_REGION", os.environ.get("AWS_REGION", "us-east-1")).strip()


def _sms_message_attributes() -> dict:
    return {
        "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
    }


def dispatch_sms(phone: str, message: str, *, incident_id: str | None = None) -> dict:
    topic_arn = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    sns = boto3.client("sns", region_name=_aws_region())
    attrs = _sms_message_attributes()
    if incident_id:
        attrs["incident_id"] = {"DataType": "String", "StringValue": incident_id}
    if topic_arn:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="PITER Escalation",
            MessageAttributes=attrs,
        )
    else:
        response = sns.publish(
            PhoneNumber=phone,
            Message=message,
            MessageAttributes=attrs,
        )
    logger.info("sns_sms_sent message_id=%s topic=%s", response.get("MessageId"), bool(topic_arn))
    return {"channel": "sms", "message_id": response.get("MessageId"), "sent": True}


def dispatch_email(
    to: str,
    subject: str,
    body: str,
    *,
    incident_id: str | None = None,
) -> dict:
    sender = os.environ.get("PITER_SES_SENDER_EMAIL", "").strip().strip("<>")
    if not sender:
        raise NotificationDispatchError(
            "ses_not_configured",
            "PITER_SES_SENDER_EMAIL is not configured",
        )
    ses = boto3.client("ses", region_name=_aws_region())
    email_kwargs: dict = {
        "Source": sender,
        "Destination": {"ToAddresses": [to]},
        "Message": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
        },
    }
    config_set = os.environ.get("PITER_SES_CONFIGURATION_SET", "").strip()
    if config_set:
        email_kwargs["ConfigurationSetName"] = config_set
    reply_to = os.environ.get("PITER_SES_REPLY_TO", "").strip()
    if reply_to:
        email_kwargs["ReplyToAddresses"] = [reply_to]
    if incident_id:
        email_kwargs["Tags"] = [{"Name": "incident_id", "Value": incident_id[:256]}]
    response = ses.send_email(**email_kwargs)
    logger.info("ses_email_sent message_id=%s config_set=%s", response.get("MessageId"), bool(config_set))
    return {"channel": "email", "message_id": response.get("MessageId"), "sent": True}


def dispatch_live(
    recipient: str,
    message: str,
    *,
    subject: str | None = None,
    incident_id: str | None = None,
) -> dict:
    if not live_dispatch_enabled():
        raise NotificationDispatchError(
            "live_dispatch_disabled",
            "PITER_ENABLE_LIVE_DISPATCH is not true",
        )
    if recipient.startswith("+"):
        return dispatch_sms(recipient, message, incident_id=incident_id)
    if "@" in recipient:
        return dispatch_email(
            recipient,
            subject or "PITER escalation",
            message,
            incident_id=incident_id,
        )
    raise NotificationDispatchError(
        "unknown_channel",
        "Recipient must be an E.164 phone (+...) or email address",
    )


def dispatch_live_safe(
    recipient: str,
    message: str,
    *,
    subject: str | None = None,
    incident_id: str | None = None,
) -> dict:
    """Dispatch or raise NotificationDispatchError / ClientError."""
    try:
        return dispatch_live(
            recipient,
            message,
            subject=subject,
            incident_id=incident_id,
        )
    except ClientError as exc:
        raise NotificationDispatchError(
            "aws_dispatch_failed",
            str(exc.response.get("Error", {}).get("Message", exc)),
        ) from exc
