# Notifications

Escalation notifications default to **mock** mode. SNS and SES dispatch only when every safety gate passes and `PITER_ENABLE_LIVE_DISPATCH=true`.

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
PITER_SNS_TOPIC_ARN=
PITER_SES_SENDER_EMAIL=
PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT=1
```

## Modes

| Mode | Behavior |
|---|---|
| `mock` | Preview only; `sent: false`; masked recipients in UI |
| `preview` | Policy and recipient mask; no external dispatch |
| `live` | Calls SNS/SES when `PITER_ENABLE_LIVE_DISPATCH=true` and all gates pass |

## UI flow

1. Run Alert Storm → PITER triage workflow.
2. Click **Escalate on-call** on the P1 card or post-demo escalation panel.
3. Enter `PITER_NOTIFICATION_CONFIRMATION_TOKEN` from your local `.env`.
4. Send SMS and/or email — recipients come from `PITER_DEMO_SMS_RECIPIENT` / `PITER_DEMO_EMAIL_RECIPIENT` only (never from browser input).

API: `POST /api/escalation/notify` with `{ channel, incident_id, service, severity, confirmation_token }`.

Bootstrap exposes `notification.live_dispatch_enabled`, `sms_configured`, `email_configured`, and `allowlist_count`.

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

## AWS setup checklist

Use profile `reemmor` (or your local profile) in `us-east-1`.

### SES (email)

1. Verify sender identity in SES → set `PITER_SES_SENDER_EMAIL`.
2. If the account is in **SES sandbox**, verify the recipient email too, or request production access.
3. Add recipient to `PITER_NOTIFICATION_ALLOWLIST`.

### SNS (SMS)

1. Confirm SMS spending limit / regional support in SNS SMS preferences.
2. For direct SMS, leave `PITER_SNS_TOPIC_ARN` empty; add E.164 phone to allowlist.
3. Optional: publish via `PITER_SNS_TOPIC_ARN` instead of direct `PhoneNumber`.

### Local `.env` example (do not commit)

```env
PITER_NOTIFICATION_MODE=live
PITER_ENABLE_LIVE_DISPATCH=true
PITER_NOTIFICATION_CONFIRMATION_TOKEN=your-secret-token
PITER_NOTIFICATION_ALLOWLIST=+15551234567,ops@example.com
PITER_DEMO_SMS_RECIPIENT=+15551234567
PITER_DEMO_EMAIL_RECIPIENT=ops@example.com
PITER_SES_SENDER_EMAIL=noreply@yourdomain.com
```

## Safety

- Do not commit real phone numbers, personal emails, or confirmation tokens.
- Tests mock boto3; CI keeps `PITER_ENABLE_LIVE_DISPATCH=false` by default.
- See [`action_groups/piter-escalation/lambda_function.py`](../action_groups/piter-escalation/lambda_function.py) and [`app/services/notification_dispatch.py`](../app/services/notification_dispatch.py).
