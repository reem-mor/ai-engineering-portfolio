# PITER Escalation, SNS, and SES Live Check

**Date:** 2026-06-08

## Default safety

| Gate | Expected | Verified |
|------|----------|----------|
| Default mode | mock or preview | Bootstrap `notification.mode` from env |
| Live dispatch | Requires all gates | `live_dispatch_enabled()` |
| Confirmation token | Required for live | API returns 403 without token |
| Allowlist | Enforced | Tests in `test_notification_dispatch.py` |
| Idempotency | Per incident+channel | Fixed frontend key `{incidentId}:{channel}` |
| Masked recipients in UI | Yes | Modal shows preview only |
| No real SMS/email this run | **Confirmed** | No live send executed |

## UI

- Settings page shows notification mode and delivery readiness
- Escalation modal: **Escalate on-call (SMS / email)** — preview/mock unless live gates satisfied
- Screenshot: `screenshots/final/09_escalation_preview.png`

## SMS sandbox / SES

Documented in `PITER_SNS_SES_AWS_CHECK.md` — sender verification and sandbox limits apply.

## Do not enable live without

`PITER_NOTIFICATION_MODE=live` + confirmation + allowlist + P1/P2 severity + verified SES/SNS + explicit operator confirm.
