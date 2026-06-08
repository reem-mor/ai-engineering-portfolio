# PITER AWS Phase 9 — SNS and SES Verification

**Audit date:** 2026-06-08  
**No messages sent during this audit.**

## Local notification configuration

| Variable | Status |
|----------|--------|
| `PITER_NOTIFICATION_MODE` | `live` |
| `PITER_ENABLE_LIVE_DISPATCH` | `true` |
| `PITER_NOTIFICATION_REQUIRE_CONFIRMATION` | `true` |
| `PITER_NOTIFICATION_CONFIRMATION_TOKEN` | Set (not recorded) |
| `PITER_NOTIFICATION_ALLOWLIST` | Set (SMS + emails; masked) |
| `PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT` | `1` (default) |
| `PITER_SNS_TOPIC_ARN` | `arn:aws:sns:us-east-1:329***579:piter-aiops-escalation` |
| `PITER_SES_SENDER_EMAIL` | `fo***@gmail.com` |
| `PITER_SES_CONFIGURATION_SET` | `piter-aiops-escalations` |

## SNS topic

| Check | Result |
|-------|--------|
| Topic exists | **Yes** — `piter-aiops-escalation` |
| Subscriptions confirmed | **1** |
| Subscriptions pending | 0 |
| Protocol | **sms** |
| Endpoint | `+972***7754` (masked) |

## SMS sandbox

| Check | Result |
|-------|--------|
| `get-sms-sandbox-account-status` | **`IsInSandbox: true`** |

**Implication:** SMS can only reach **verified sandbox destinations**. Demo recipient must be verified in SNS SMS sandbox.

## SES

| Identity | Verification |
|----------|--------------|
| `fo***@gmail.com` (sender) | **Success** |
| `re***@gmail.com` (secondary) | **Success** |
| Account sending enabled | **true** |

**Note:** SES may still be in sandbox mode for unverified recipients (not explicitly queried; assume sandbox unless production access granted).

## IAM permissions (inferred)

Dispatcher uses boto3 SNS/SES clients (`app/services/notification_dispatch.py`):

- `sns:Publish` (topic or direct SMS)
- `ses:SendEmail` / `ses:SendRawEmail`
- `sns:ListSubscriptionsByTopic` for SMS preflight

Agent/Lambda role would need same if `piter-escalation` is deployed.

## Local safety gates

| Gate | Implementation |
|------|----------------|
| Live dispatch off by default in `.env.example` | `PITER_ENABLE_LIVE_DISPATCH=false` |
| Confirmation token required | UI + `piter-escalation` Lambda checks token |
| Allowlist enforcement | `PITER_NOTIFICATION_ALLOWLIST` |
| Duplicate send prevention | `PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT=1` in routes |
| Severity filter | `PITER_NOTIFICATION_ALLOWED_SEVERITIES=P1,P2` |

## Demo recipient verification

Before live SMS demo:

1. Confirm demo phone is **verified in SNS SMS sandbox**.
2. Confirm recipient email is **verified in SES** if not using sandbox production access.
3. Enter confirmation token in UI before send.

## Commands run (read-only)

```powershell
aws sns list-topics
aws sns get-topic-attributes --topic-arn arn:aws:sns:us-east-1:329597159579:piter-aiops-escalation
aws sns list-subscriptions-by-topic --topic-arn arn:aws:sns:us-east-1:329597159579:piter-aiops-escalation
aws sns get-sms-sandbox-account-status
aws ses list-identities
aws ses get-identity-verification-attributes --identities <masked emails>
aws ses get-account-sending-enabled
```

**No Publish, SendEmail, or SendSMS calls made.**
