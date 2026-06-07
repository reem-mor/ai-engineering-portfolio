"""Boto3 SNS/SES dispatch and optional WhatsApp for live escalation."""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

SMS_CONSOLE_URL = (
    "https://us-east-1.console.aws.amazon.com/sms-voice/home?region=us-east-1#/overview"
)
SMS_BILLING_RESUBSCRIBE_URL = (
    "https://portal.aws.amazon.com/billing/signup?type=resubscribe#/resubscribed"
)


class NotificationDispatchError(Exception):
    """Raised when live notification dispatch is blocked or misconfigured."""

    def __init__(self, code: str, message: str, *, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
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
    return bool(os.environ.get("PITER_DEMO_SMS_RECIPIENT", "").strip()) or bool(
        os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    )


def whatsapp_provider() -> str:
    return os.environ.get("PITER_WHATSAPP_PROVIDER", "callmebot").strip().lower()


def whatsapp_configured() -> bool:
    phone = os.environ.get("PITER_DEMO_WHATSAPP_RECIPIENT", "").strip() or os.environ.get(
        "PITER_DEMO_SMS_RECIPIENT", ""
    ).strip()
    if not phone.startswith("+"):
        return False
    provider = whatsapp_provider()
    if provider == "cloud":
        return bool(
            os.environ.get("PITER_WHATSAPP_ACCESS_TOKEN", "").strip()
            and os.environ.get("PITER_WHATSAPP_PHONE_NUMBER_ID", "").strip()
        )
    return bool(os.environ.get("PITER_WHATSAPP_API_KEY", "").strip())


def allowlist_count() -> int:
    raw = os.environ.get("PITER_NOTIFICATION_ALLOWLIST", "")
    return len({item.strip() for item in raw.split(",") if item.strip()})


def sms_use_topic() -> bool:
    return os.environ.get("PITER_SNS_SMS_USE_TOPIC", "false").lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def sms_preflight_enabled() -> bool:
    default = "true" if live_dispatch_enabled() else "false"
    return os.environ.get("PITER_SMS_PREFLIGHT_CHECK", default).lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def _aws_region() -> str:
    return os.environ.get("PITER_AWS_REGION", os.environ.get("AWS_REGION", "us-east-1")).strip()


def _sms_message_attributes() -> dict:
    return {
        "AWS.SNS.SMS.SMSType": {"DataType": "String", "StringValue": "Transactional"},
    }


def _pinpoint_not_enabled(message: str) -> bool:
    return "PinpointSmsVoiceV2" in message or "SubscriptionRequiredException" in message


def _confirmed_sms_subscriptions(topic_arn: str, *, region: str | None = None) -> list[dict]:
    sns = boto3.client("sns", region_name=region or _aws_region())
    confirmed: list[dict] = []
    for page in sns.get_paginator("list_subscriptions_by_topic").paginate(TopicArn=topic_arn):
        for item in page.get("Subscriptions", []):
            arn = str(item.get("SubscriptionArn") or "")
            if item.get("Protocol") != "sms":
                continue
            if not arn.startswith("arn:aws:sns:"):
                continue
            confirmed.append(item)
    return confirmed


def _check_sms_topic_route(*, phone: str | None = None, region: str | None = None) -> dict:
    """SMS via SNS topic fan-out (works when End User Messaging API status is unavailable)."""
    topic_arn = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    if not topic_arn:
        return {"ready": False, "reason": "no_topic_arn"}

    try:
        confirmed = _confirmed_sms_subscriptions(topic_arn, region=region)
    except ClientError as exc:
        err = exc.response.get("Error", {})
        return {
            "ready": False,
            "reason": err.get("Code") or "topic_check_failed",
            "message": err.get("Message", str(exc)),
            "topic_arn": topic_arn,
        }

    if not confirmed:
        return {
            "ready": False,
            "reason": "topic_no_confirmed_sms",
            "message": (
                f"SNS topic {topic_arn} has no confirmed SMS subscriptions. "
                "Add your phone under Subscriptions with protocol SMS."
            ),
            "topic_arn": topic_arn,
        }

    if phone:
        phone = phone.strip()
        if not any(item.get("Endpoint") == phone for item in confirmed):
            return {
                "ready": False,
                "reason": "topic_phone_not_subscribed",
                "message": (
                    f"{phone} is not a confirmed SMS subscriber on {topic_arn}. "
                    "Subscribe the number in the SNS console."
                ),
                "topic_arn": topic_arn,
            }

    return {
        "ready": True,
        "reason": None,
        "message": None,
        "route": "topic",
        "topic_arn": topic_arn,
        "confirmed_subscribers": len(confirmed),
        "console_url": SMS_CONSOLE_URL,
    }


def _sms_publish_route(phone: str) -> str:
    topic_arn = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    if not topic_arn:
        return "direct"
    if not check_sms_account_ready(phone=phone).get("ready"):
        return "direct"
    if sms_use_topic() or _check_sms_topic_route(phone=phone).get("ready"):
        return "topic"
    return "direct"


def check_sms_account_ready(*, region: str | None = None, phone: str | None = None) -> dict:
    """Probe whether this AWS account can deliver SMS (End User Messaging enabled)."""
    sns = boto3.client("sns", region_name=region or _aws_region())
    topic_arn = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    topic_status = _check_sms_topic_route(phone=phone, region=region) if topic_arn else None
    try:
        response = sns.get_sms_attributes(attributes=["MonthlySpendLimit", "DefaultSMSType"])
        attrs = response.get("attributes", {})
        spend = str(attrs.get("MonthlySpendLimit", "")).strip()
        if spend in {"", "0"}:
            return {
                "ready": False,
                "reason": "sms_spend_limit_zero",
                "message": (
                    "AWS SMS monthly spend limit is unset or zero. Open End User Messaging, "
                    "accept the SMS terms, and set a monthly spend limit (e.g. $10)."
                ),
                "console_url": SMS_CONSOLE_URL,
                "attributes": attrs,
            }
        route = "topic" if topic_status and topic_status.get("ready") else "direct"
        return {
            "ready": True,
            "reason": None,
            "message": None,
            "route": route,
            "console_url": SMS_CONSOLE_URL,
            "attributes": attrs,
            **(
                {
                    "topic_arn": topic_status.get("topic_arn"),
                    "confirmed_subscribers": topic_status.get("confirmed_subscribers"),
                }
                if topic_status and topic_status.get("ready")
                else {}
            ),
        }
    except ClientError as exc:
        err = exc.response.get("Error", {})
        code = err.get("Code", "")
        message = err.get("Message", str(exc))
        if _pinpoint_not_enabled(message) or code == "UserError":
            details: dict = {
                "ready": False,
                "reason": "sms_service_not_enabled",
                "message": (
                    "AWS End User Messaging SMS is not enabled. SNS may return MessageId but "
                    "CloudWatch shows 0 deliveries until you accept SMS terms and set a spend "
                    "limit in the console. A confirmed SNS topic subscription is not enough."
                ),
                "console_url": SMS_CONSOLE_URL,
                "billing_url": SMS_BILLING_RESUBSCRIBE_URL,
            }
            if topic_status and topic_status.get("ready"):
                details["topic_subscribers"] = topic_status.get("confirmed_subscribers")
                details["topic_arn"] = topic_status.get("topic_arn")
            return details
        return {
            "ready": False,
            "reason": code or "sms_check_failed",
            "message": message,
            "console_url": SMS_CONSOLE_URL,
        }


def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: dict | None = None,
    timeout: float = 30.0,
) -> dict:
    data = None
    req_headers = dict(headers or {})
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            if not raw.strip():
                return {"status": response.status}
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"body": raw}
            if isinstance(parsed, dict):
                parsed.setdefault("status", response.status)
                return parsed
            return {"status": response.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise NotificationDispatchError(
            "whatsapp_http_error",
            f"WhatsApp API HTTP {exc.code}: {detail[:500]}",
        ) from exc
    except urllib.error.URLError as exc:
        raise NotificationDispatchError(
            "whatsapp_network_error",
            f"WhatsApp API request failed: {exc.reason}",
        ) from exc


def dispatch_whatsapp_callmebot(phone: str, message: str) -> dict:
    api_key = os.environ.get("PITER_WHATSAPP_API_KEY", "").strip()
    if not api_key:
        raise NotificationDispatchError(
            "whatsapp_not_configured",
            "Set PITER_WHATSAPP_API_KEY (CallMeBot API key from WhatsApp registration).",
        )
    query = urllib.parse.urlencode(
        {
            "phone": phone,
            "text": message[:1500],
            "apikey": api_key,
            "source": "piter-aiops",
        }
    )
    url = f"https://api.callmebot.com/whatsapp.php?{query}"
    result = _http_json(url)
    logger.info("whatsapp_callmebot_sent phone=%s", f"{phone[:4]}***{phone[-2:]}")
    return {
        "channel": "whatsapp",
        "provider": "callmebot",
        "message_id": str(result.get("status", "ok")),
        "sent": True,
    }


def dispatch_whatsapp_cloud(phone: str, message: str) -> dict:
    token = os.environ.get("PITER_WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_number_id = os.environ.get("PITER_WHATSAPP_PHONE_NUMBER_ID", "").strip()
    if not token or not phone_number_id:
        raise NotificationDispatchError(
            "whatsapp_not_configured",
            "Set PITER_WHATSAPP_ACCESS_TOKEN and PITER_WHATSAPP_PHONE_NUMBER_ID.",
        )
    to_digits = phone.lstrip("+").replace(" ", "").replace("-", "")
    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_digits,
        "type": "text",
        "text": {"preview_url": False, "body": message[:4096]},
    }
    result = _http_json(
        url,
        method="POST",
        headers={"Authorization": f"Bearer {token}"},
        body=payload,
    )
    messages = result.get("messages") or []
    message_id = messages[0].get("id") if messages else result.get("status")
    logger.info("whatsapp_cloud_sent message_id=%s phone=%s", message_id, f"{phone[:4]}***{phone[-2:]}")
    return {
        "channel": "whatsapp",
        "provider": "cloud",
        "message_id": message_id,
        "sent": True,
    }


def dispatch_whatsapp(phone: str, message: str, *, incident_id: str | None = None) -> dict:
    phone = phone.strip()
    if not phone.startswith("+"):
        raise NotificationDispatchError(
            "invalid_phone",
            "WhatsApp recipient must be E.164 format starting with +",
        )
    if not whatsapp_configured():
        raise NotificationDispatchError(
            "whatsapp_not_configured",
            "WhatsApp is not configured. Set PITER_WHATSAPP_API_KEY (CallMeBot) or Meta Cloud API vars.",
        )
    provider = whatsapp_provider()
    if provider == "cloud":
        return dispatch_whatsapp_cloud(phone, message)
    return dispatch_whatsapp_callmebot(phone, message)


def dispatch_sms(phone: str, message: str, *, incident_id: str | None = None) -> dict:
    phone = phone.strip()
    if not phone.startswith("+"):
        raise NotificationDispatchError(
            "invalid_phone",
            "SMS recipient must be E.164 format starting with +",
        )

    if sms_preflight_enabled():
        status = check_sms_account_ready(phone=phone)
        if not status.get("ready"):
            if whatsapp_configured():
                logger.warning("sms_unavailable_falling_back_to_whatsapp reason=%s", status.get("reason"))
                result = dispatch_whatsapp(phone, message, incident_id=incident_id)
                result["fallback_from"] = "sms"
                return result
            raise NotificationDispatchError(
                str(status.get("reason") or "sms_not_ready"),
                str(status.get("message") or "SMS delivery is not available on this AWS account"),
                details={"console_url": status.get("console_url"), **status},
            )

    topic_arn = os.environ.get("PITER_SNS_TOPIC_ARN", "").strip()
    sns = boto3.client("sns", region_name=_aws_region())
    attrs = _sms_message_attributes()
    if incident_id:
        attrs["incident_id"] = {"DataType": "String", "StringValue": incident_id}

    route = _sms_publish_route(phone)
    if route == "topic" and topic_arn:
        response = sns.publish(
            TopicArn=topic_arn,
            Message=message,
            MessageAttributes=attrs,
        )
    else:
        response = sns.publish(
            PhoneNumber=phone,
            Message=message,
            MessageAttributes=attrs,
        )
        route = "direct"

    logger.info(
        "sns_sms_sent message_id=%s route=%s phone=%s",
        response.get("MessageId"),
        route,
        f"{phone[:4]}***{phone[-2:]}" if len(phone) > 6 else "***",
    )
    return {
        "channel": "sms",
        "message_id": response.get("MessageId"),
        "sent": True,
        "route": route,
    }


def dispatch_email(
    to: str,
    subject: str,
    body: str,
    *,
    html_body: str | None = None,
    incident_id: str | None = None,
) -> dict:
    sender = os.environ.get("PITER_SES_SENDER_EMAIL", "").strip().strip("<>")
    if not sender:
        raise NotificationDispatchError(
            "ses_not_configured",
            "PITER_SES_SENDER_EMAIL is not configured",
        )
    ses = boto3.client("ses", region_name=_aws_region())
    body_payload: dict = {"Text": {"Data": body, "Charset": "UTF-8"}}
    if html_body:
        body_payload["Html"] = {"Data": html_body, "Charset": "UTF-8"}
    email_kwargs: dict = {
        "Source": sender,
        "Destination": {"ToAddresses": [to]},
        "Message": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": body_payload,
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
    channel: str | None = None,
    subject: str | None = None,
    html_body: str | None = None,
    incident_id: str | None = None,
) -> dict:
    if not live_dispatch_enabled():
        raise NotificationDispatchError(
            "live_dispatch_disabled",
            "PITER_ENABLE_LIVE_DISPATCH is not true",
        )
    normalized = (channel or "").strip().lower()
    if normalized == "whatsapp":
        return dispatch_whatsapp(recipient, message, incident_id=incident_id)
    if normalized == "sms" or (not normalized and recipient.startswith("+")):
        return dispatch_sms(recipient, message, incident_id=incident_id)
    if normalized == "email" or "@" in recipient:
        return dispatch_email(
            recipient,
            subject or "PITER escalation",
            message,
            html_body=html_body,
            incident_id=incident_id,
        )
    raise NotificationDispatchError(
        "unknown_channel",
        "Recipient must be email, or phone for sms/whatsapp",
    )


def dispatch_live_safe(
    recipient: str,
    message: str,
    *,
    channel: str | None = None,
    subject: str | None = None,
    html_body: str | None = None,
    incident_id: str | None = None,
) -> dict:
    """Dispatch or raise NotificationDispatchError / ClientError."""
    try:
        return dispatch_live(
            recipient,
            message,
            channel=channel,
            subject=subject,
            html_body=html_body,
            incident_id=incident_id,
        )
    except ClientError as exc:
        raise NotificationDispatchError(
            "aws_dispatch_failed",
            str(exc.response.get("Error", {}).get("Message", exc)),
        ) from exc
