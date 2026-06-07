# PITER AiOps — Notifications (SNS/SES/WhatsApp) Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Modes
| Mode | Behavior |
| ---- | -------- |
| `mock` (default) | no sending; returns simulated result |
| `preview` | masked recipients + message preview, no sending (`operation=preview`) |
| `live` | sends only when explicitly enabled **and** confirmed |

## Live-send gate (all required)
Implemented in `action_groups/piter-escalation/lambda_function.py` +
`app/services/notification_dispatch.py`:
- `PITER_NOTIFICATION_MODE=live` **and** `PITER_ENABLE_LIVE_DISPATCH=true`
- valid confirmation token (`PITER_NOTIFICATION_REQUIRE_CONFIRMATION` default true)
- recipient on allowlist (`PITER_NOTIFICATION_ALLOWLIST`)
- severity allowed (`PITER_NOTIFICATION_ALLOWED_SEVERITIES`, e.g. P1/approved P2)
- not already sent (idempotency: `SENT_IDEMPOTENCY_KEYS`, key `incident:recipient:severity`)
- `PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT` (default 1)
- SES sender verified / SNS configured (SMS preflight `check_sms_account_ready`)

## Masking
- Escalation Lambda `_mask_recipient`: `xx***xx`.
- Dispatch logs mask phone: `f"{phone[:4]}***{phone[-2:]}"`.
- Recommendation: align to task examples (`+972-**-***-5754`, `r***@gmail.com`) — minor polish.

## Env contract (no hardcoded values after Commit 2)
```
PITER_NOTIFICATION_MODE=mock
PITER_NOTIFICATION_REQUIRE_CONFIRMATION=true
PITER_DEMO_SMS_RECIPIENT=
PITER_DEMO_EMAIL_RECIPIENT=
PITER_DEMO_WHATSAPP_RECIPIENT=
PITER_SNS_TOPIC_ARN=
PITER_SES_SENDER_EMAIL=
PITER_NOTIFICATION_MAX_SENDS_PER_INCIDENT=1
PITER_NOTIFICATION_ALLOWLIST=
PITER_NOTIFICATION_ALLOWED_SEVERITIES=P1,P2
```

## Safety findings
| Item | Status |
| ---- | ------ |
| Mock by default | PASS |
| No real send in tests | PASS (`test_notification_dispatch.py` asserts gating) |
| No hardcoded recipients | PASS after Commit 2 (was: phone/email defaults in scripts/docs) |
| Idempotency | PASS |
| Confirmation enforced | PASS |
| Graceful offline (no creds) | PASS (fix to `check_sms_account_ready`) |
| UI shows mode/masked recipient/confirmation/delivery/idempotency | PASS (bootstrap `_notification_settings`) |

## Status: PASS — demo-capable and safe; PII removed in Commit 2.
