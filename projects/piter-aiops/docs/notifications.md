# Notifications (SNS + SES)

Escalation notifications default to **mock** mode. Live SNS/SES dispatch requires explicit gates and `PITER_ENABLE_LIVE_DISPATCH=true`.

## One-command AWS setup

From `projects/piter-aiops`:

```powershell
python scripts/setup_notifications.py --sender-email reem.mor3@gmail.com --verify-recipients reem.mor3@gmail.com
```

For demo to a teacher (SES sandbox — both must verify):

```powershell
python scripts/setup_notifications.py `
  --sender-email reem.mor3@gmail.com `
  --verify-recipients teacher@school.edu
```

The script creates (idempotent):

| Resource | Name | Purpose |
|----------|------|---------|
| SNS topic | `piter-aiops-escalation` | Optional fan-out; **direct SMS is default** (see `PITER_SNS_SMS_USE_TOPIC`) |
| SES configuration set | `piter-aiops-escalations` | Bounce/complaint metrics in CloudWatch |
| SES identities | sender + recipients | Required before send; sandbox needs all recipients verified |
| IAM policy | `PITER-AiOps-Notifications` | Least privilege for Lambda/EC2 role |

Attach IAM policy to your runtime role:

```powershell
aws iam attach-role-policy `
  --role-name "PITER AiOps-lambda-role" `
  --policy-arn arn:aws:iam::329597159579:policy/PITER-AiOps-Notifications `
  --profile reemmor
```

Local dev with `admin-reem` already has full access; the policy matters for EC2/Lambda in production.

## Environment variables

```env
PITER_NOTIFICATION_MODE=mock          # mock | preview | live
PITER_ENABLE_LIVE_DISPATCH=false      # explicit opt-in for boto3 SNS/SES
PITER_NOTIFICATION_REQUIRE_CONFIRMATION=true
PITER_NOTIFICATION_CONFIRMATION_TOKEN=
PITER_NOTIFICATION_ALLOWLIST=
PITER_NOTIFICATION_ALLOWED_SEVERITIES=P1,P2
PITER_DEMO_SMS_RECIPIENT=
PITER_DEMO_EMAIL_RECIPIENT=
PITER_SNS_TOPIC_ARN=                  # optional topic for fan-out
PITER_SNS_SMS_USE_TOPIC=false         # true = publish to topic; false = direct PhoneNumber (default)
PITER_SMS_PREFLIGHT_CHECK=true        # block SMS if AWS End User Messaging is not enabled
PITER_SES_SENDER_EMAIL=
PITER_SES_CONFIGURATION_SET=piter-aiops-escalations
PITER_SES_REPLY_TO=                   # optional Reply-To header
PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT=1
```

## Modes

| Mode | Behavior |
|---|---|
| `mock` | Preview only; `sent: false`; masked recipients in UI |
| `preview` | Policy and recipient mask; no external dispatch |
| `live` | Calls SNS/SES when `PITER_ENABLE_LIVE_DISPATCH=true` and all gates pass |

## Best practices (implemented)

- **SMS**: `AWS.SNS.SMS.SMSType=Transactional`, monthly spend limit set by setup script (default $1).
- **Email**: configuration set for delivery/bounce tracking; optional `Reply-To`; incident tags for SES metrics.
- **IAM**: scoped `sns:Publish` to topic + SMS-only publish; `ses:SendEmail` limited to verified identity ARN.
- **App safety**: allowlist, confirmation token, idempotency, severity gate — unchanged.

## UI flow

1. Run Alert Storm → PITER triage workflow.
2. Click **Escalate on-call** on the P1 card or post-demo escalation panel.
3. Enter `PITER_NOTIFICATION_CONFIRMATION_TOKEN` from your local `.env`.
4. Send **WhatsApp**, SMS, and/or email — recipients come from demo env vars only (never from browser input).

API: `POST /api/escalation/notify` with `{ channel, incident_id, service, severity, confirmation_token }` where `channel` is `sms`, `email`, or `whatsapp`.

Bootstrap exposes `notification.live_dispatch_enabled`, `sms_configured`, `sms_delivery_ready`, `whatsapp_configured`, `demo_whatsapp_configured`, `email_configured`, and `allowlist_count`.

## WhatsApp (CallMeBot — no AWS SMS required)

When AWS End User Messaging SMS is not enabled, use WhatsApp for demo escalations via [CallMeBot](https://www.callmebot.com/blog/free-api-whatsapp-messages/) (personal use, free tier).

**Important:** CallMeBot’s free bot is often **full** — the official page may hide the phone number entirely. If you never get a reply, that is usually why (not a mistake on your side).

**One-time setup on your phone:**

1. Open the [CallMeBot WhatsApp setup page](https://www.callmebot.com/blog/free-api-whatsapp-messages/) and use the **current** bot number shown there (numbers rotate when bots fill up).
2. If the page says “bot is full”, try these alternate registration numbers (one at a time):
   - `+34 623 78 64 49`
   - `+34 644 66 32 62`
   - `+34 621 08 34 84`
3. Add the number to contacts, then send **exactly** (copy/paste):
   ```
   I allow callmebot to send me messages
   ```
4. If you registered before, try: `Recover APIKey`
5. Wait up to 2 minutes. If nothing, wait 24h and retry, or message Telegram **@callmebot_com**.

When it works, you get: `API Activated for your phone number. Your APIKEY is 123123`

6. Add to `.env` (do not commit):

```env
PITER_WHATSAPP_PROVIDER=callmebot
PITER_WHATSAPP_API_KEY=<your-key-from-callmebot>
PITER_DEMO_WHATSAPP_RECIPIENT=+972526775754
```

Phone must be in `PITER_NOTIFICATION_ALLOWLIST`. Restart Flask after updating `.env`.

**If CallMeBot keeps failing:** use **email** (already works), enable **AWS SMS** in the console (see below), or use Meta/Twilio WhatsApp Cloud API for production (`PITER_WHATSAPP_PROVIDER=cloud`).

Test:

```powershell
python scripts/test_live_notify.py
```

If SMS preflight fails but WhatsApp is configured, **Send SMS** in the UI automatically falls back to WhatsApp.

**Meta Cloud API** (production): set `PITER_WHATSAPP_PROVIDER=cloud`, `PITER_WHATSAPP_ACCESS_TOKEN`, and `PITER_WHATSAPP_PHONE_NUMBER_ID`.

## SMS not arriving (common fix)

SNS `Publish` can return a `MessageId` even when **AWS End User Messaging SMS** is not enabled. New accounts must opt in once:

1. Open [End User Messaging SMS console](https://us-east-1.console.aws.amazon.com/sms-voice/home?region=us-east-1#/overview) (us-east-1).
2. Accept SMS terms and set **Monthly spend limit** (e.g. $10).
3. In **SMS sandbox**, add and verify your destination phone (`PITER_DEMO_SMS_RECIPIENT`).
4. Run `python scripts/diagnose_sms.py` — must report `"ready": true`.
5. Test: `python scripts/test_live_notify.py`.

Direct publish to `PhoneNumber` is the default. Set `PITER_SNS_SMS_USE_TOPIC=true` only if you intentionally fan out via SNS topic.

## Safety gates (live_notify)

All must pass before boto3 dispatch:

1. `PITER_NOTIFICATION_MODE=live`
2. `PITER_ENABLE_LIVE_DISPATCH=true`
3. `PITER_NOTIFICATION_REQUIRE_CONFIRMATION=true`
4. Matching `confirmation_token`
5. Recipient in `PITER_NOTIFICATION_ALLOWLIST`
6. Severity in `PITER_NOTIFICATION_ALLOWED_SEVERITIES`
7. Email: `PITER_SES_SENDER_EMAIL` set; SMS: optional `PITER_SNS_TOPIC_ARN` or direct phone publish
8. Idempotency key not already sent

## SES sandbox checklist

1. Run `setup_notifications.py` with `--sender-email` and `--verify-recipients`.
2. Click AWS verification links in each inbox.
3. Confirm: `aws sesv2 get-email-identity --email-identity you@example.com --region us-east-1 --profile reemmor`
4. Request **production access** in SES console when you need to email unverified addresses.

## Local `.env` example (do not commit)

```env
PITER_NOTIFICATION_MODE=live
PITER_ENABLE_LIVE_DISPATCH=true
PITER_NOTIFICATION_CONFIRMATION_TOKEN=your-secret-token
PITER_NOTIFICATION_ALLOWLIST=+15551234567,ops@example.com
PITER_DEMO_SMS_RECIPIENT=+15551234567
PITER_DEMO_EMAIL_RECIPIENT=ops@example.com
PITER_SES_SENDER_EMAIL=noreply@yourdomain.com
PITER_SES_CONFIGURATION_SET=piter-aiops-escalations
PITER_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:piter-aiops-escalation
```

## Safety

- Do not commit real phone numbers, personal emails, or confirmation tokens.
- Tests mock boto3; CI keeps `PITER_ENABLE_LIVE_DISPATCH=false` by default.
- See [`action_groups/piter-escalation/lambda_function.py`](../action_groups/piter-escalation/lambda_function.py) and [`app/services/notification_dispatch.py`](../app/services/notification_dispatch.py).
