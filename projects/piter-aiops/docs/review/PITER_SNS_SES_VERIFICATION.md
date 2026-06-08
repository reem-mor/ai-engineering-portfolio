# PITER SNS/SES Verification

**Date:** 2026-06-08  
**Mode default:** `mock` / `preview` — **no live messages sent during mutation**

## SNS

| Item | Status |
|------|--------|
| Topic | `piter-aiops-escalation` |
| Subscription | SMS endpoint present (masked `+97252***5754`) |
| Live publish during tests | **None** |

## SES

| Item | Status |
|------|--------|
| Production access | **false** (sandbox) |
| Verified identities | 2 Gmail senders (masked) |
| Live email during tests | **None** |

## App + Lambda gates

| Gate | Default |
|------|---------|
| `PITER_NOTIFICATION_MODE` | `mock` |
| `PITER_ENABLE_LIVE_DISPATCH` | `false` |
| `PITER_NOTIFICATION_REQUIRE_CONFIRMATION` | `true` |
| Allowlist / token in Lambda env | **empty** |

Live send requires all: mode=live, dispatch enabled, valid token, allowlisted recipient, allowed severity, idempotency slot, verified SES sender.

## Demo guidance

- Escalation UI shows **preview/mock** payloads with masked recipients
- For teacher demo SMS: verify recipient in SNS sandbox first; set live gates explicitly in local `.env` only — never commit

See [`docs/notifications.md`](../notifications.md).
