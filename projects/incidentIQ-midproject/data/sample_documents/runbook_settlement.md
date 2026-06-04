# Runbook: Settlement service latency or failures (NJ-DGE)

**Severity:** P1  
**Applies to:** `settlement-svc` in environment `NJ-DGE` and dependent payment rails  
**Alert:** `SettlementLatencyHigh` — p95 settlement time > 30s or error rate > 2%

## Symptoms

- Settlement batches stuck in `PENDING` state in the ledger dashboard.
- Spike in `settlement_errors_total` with reason `PSP_TIMEOUT` or `DB_LOCK_WAIT`.
- Downstream reports show delayed player payouts (regulated reporting window).

## Recommended steps

1. Confirm alert scope: environment `NJ-DGE`, service `settlement-svc`, time window vs. deploys.
2. Check settlement queue depth and oldest unprocessed batch age.
3. Verify Postgres primary health (`runbook_db_cpu.md`) — settlement is DB-heavy.
4. Inspect recent deploys to `settlement-svc` and `postgres` in the last 6 hours.
5. If PSP webhook backlog exists, pause new batch submission until backlog drains.
6. Escalate to Payments on-call if error rate > 5% for 10 minutes.

## Escalation

- **Tier-1:** Steps 1–4 when no financial duplicate-risk.
- **Payments on-call:** PSP errors, duplicate settlement risk, or regulatory SLA breach.
- **P1:** Player funds movement blocked > 15 minutes in `NJ-DGE`.

## Regulatory note

NJ-DGE requires settlement reconciliation within the published SLA. Document incident start/end times for compliance audit.

## Related documents

- `payment_service_latency_runbook.txt`
- `runbook_db_cpu.md`
- `incident_history.csv` — INC-2026-NJ-001
