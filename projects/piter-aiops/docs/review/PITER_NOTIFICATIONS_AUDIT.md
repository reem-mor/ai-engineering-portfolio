# PITER SNS/SES Escalation Safety Audit

**No notifications sent during this audit.**

## Environment variables (`.env.example`)

| Variable | Purpose |
|----------|---------|
| `PITER_NOTIFICATION_MODE` | mock \| preview \| live |
| `PITER_NOTIFICATION_REQUIRE_CONFIRMATION` | Token required |
| `PITER_NOTIFICATION_CONFIRMATION_TOKEN` | Demo token |
| `PITER_DEMO_SMS_RECIPIENT` | Allowlisted SMS |
| `PITER_DEMO_EMAIL_RECIPIENT` | Allowlisted email |
| `PITER_NOTIFICATION_ALLOWLIST` | Combined allowlist |
| `PITER_SNS_TOPIC_ARN` | SNS topic |
| `PITER_SES_SENDER_EMAIL` | Verified sender |
| `PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT` | Rate limit |

## Code gates

| Gate | Location |
|------|----------|
| Mode check | `notification_dispatch.py`, `escalation_service.py` |
| Confirmation token | `routes.py` `/api/escalation/notify` |
| Severity allowlist | `PITER_NOTIFICATION_ALLOWED_SEVERITIES` |
| Recipient masking in UI | `escalation_service.mask_recipient` |
| Idempotency | Per-incident keys in dispatch + Lambda set |

## Local `.env` risk (audit finding)

Local configuration may use **`PITER_NOTIFICATION_MODE=live`** with allowlisted recipients. This is appropriate for controlled demo but:

- **Never commit `.env`** (gitignored — verified)
- Tests must not send live messages (`tests` use mocks)
- Recommend default `.env.example` to `mock` for new clones

## UI

- Bootstrap exposes `notification_mode`, SMS readiness, allowlist count
- SPA should show preview/masked recipients before send

## Gaps

1. Document SES verification + SNS sandbox in `docs/notifications.md`
2. Durable idempotency for Lambda cold starts
3. Parameter Store / Secrets Manager for recipients (production)
