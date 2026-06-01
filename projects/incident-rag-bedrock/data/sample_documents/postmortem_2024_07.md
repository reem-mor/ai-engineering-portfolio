# Postmortem: Checkout service outage — July 2024

**Incident ID:** INC-2024-0714  
**Severity:** P1  
**Duration:** 47 minutes (14:03–14:50 UTC)  
**Linked alert:** A-1042 in `alerts_last_3mo.json`

## Impact

- Checkout API 5xx rate peaked at 12% for 47 minutes.
- Estimated revenue impact during window documented in finance ticket FIN-8821.

## Root cause

An N+1 query in the checkout cart service caused database CPU saturation on `prod-db-1`. The bad deploy shipped at 13:58 UTC; alerts fired at 14:03 UTC.

## Timeline

| Time (UTC) | Event |
|------------|-------|
| 13:58 | Deploy checkout-api v2.14.0 |
| 14:03 | Alert A-1042 fired — 5xx > 2% |
| 14:15 | DBA identified long-running queries via `pg_stat_activity` |
| 14:35 | Rollback to v2.13.2 completed |
| 14:50 | Error rate below 1%; incident resolved |

## Remediation

1. Added query batching in cart service (PR #8842).
2. Added integration test for cart list endpoint load.
3. Updated `runbook_checkout_5xx.md` to check DB CPU early in triage.

## Runbooks used

- `runbook_checkout_5xx.md`
- `runbook_db_cpu.md`
