# Runbook: Checkout API 5xx rate above 2%

**Severity:** P1 when rate > 2% for 4+ minutes  
**Service:** checkout-api / API gateway  
**Alert:** `CheckoutApi5xxRate` — HTTP 5xx > 2% for 4m

## Recommended steps

1. Check recent deployments — correlate 5xx spike with the last release timestamp.
2. Check service logs — tail checkout-api and gateway logs for ERROR and stack traces.
3. Check database CPU and slow queries — run `runbook_db_cpu.md` if Postgres is hot.
4. Check dependency errors — payment service, inventory, auth token validation.
5. Roll back if the issue matches a recent bad deployment (see `deployment_rollback_sop.docx`).
6. Escalate according to severity — page checkout service owner if error rate stays above 2% for 10 minutes.

## Escalation

- **Tier-1:** Rollback when deploy correlation is clear and rollback SOP allows it.
- **Backend owner:** Persistent 5xx with no deploy correlation.
- **P1 incident channel:** Revenue-impacting checkout outage.

## Related documents

- `api_gateway_5xx_runbook.txt` — gateway-specific triage
- `postmortem_2024_07.md` — prior checkout outage (N+1 query)
- `alerts_last_3mo.json` — alert A-1042
