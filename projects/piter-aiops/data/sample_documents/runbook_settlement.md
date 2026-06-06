# RB-003: Runbook — Settlement service latency, failures, and backlog (NJ-DGE)

**Runbook ID:** RB-003  
**Severity:** P1  
**Applies to:** `settlement-svc` in `NJ-DGE`, `GIB`, and dependent payment rails  
**Alerts:** `SettlementLatencyHigh` (p95 > 30s or error rate > 2%) · `SettlementBacklogGrowing` (queue depth rising > 10 min)

## Symptoms

- Settlement batches stuck in `PENDING` state in the ledger dashboard.
- `settlement-svc` queue depth climbing; settlement latency past SLA.
- Spike in `settlement_errors_total` with reason `PSP_TIMEOUT` or `DB_LOCK_WAIT`.
- Payment confirmations delayed; charges retried via backup PSP.
- Downstream reports show delayed player payouts (regulated reporting window).

## Detection checks

1. Confirm alert scope: environment `NJ-DGE`, service `settlement-svc`, time window vs. deploys.
2. Check settlement queue depth and oldest unprocessed batch age.
3. Check `settlement-svc` dependency health: `postgres` and `payment-svc`.
4. Inspect PSP error rate and timeout metrics.
5. Verify `postgres` is not saturated — follow `runbook_db_cpu.md` first if DB-heavy.
6. Correlate recent deploys with `correlate_deployments`.

## Detection SQL

```sql
-- Pending settlement depth and age
SELECT status, count(*), max(now() - created_at) AS oldest
FROM settlements WHERE status = 'pending' GROUP BY status;
```

## Recommended steps

1. If `postgres` is the bottleneck, resolve DB saturation first (`runbook_db_cpu.md` / `runbook_connection_pool.md`).
2. If primary PSP is timing out, confirm failover to backup PSP is active (`payment_service_latency_runbook.txt`).
3. If PSP webhook backlog exists, pause new batch submission until backlog drains.
4. Drain the backlog gradually; do not replay duplicate settlements.
5. Reconcile settled vs. pending counts before declaring recovery.
6. Escalate to Payments on-call if error rate > 5% for 10 minutes.

## Dangerous actions warning

- Do NOT blindly replay the settlement queue — duplicate settlements double-charge
  customers and create a regulatory finance incident.
- Do NOT disable idempotency keys to "speed up" draining.

## Escalation

- **Tier-1:** Steps 1–4 when no financial duplicate-risk.
- **Payments on-call:** PSP errors, duplicate settlement risk, backlog growing > 15 minutes, or regulatory SLA breach.
- **P1:** Player funds movement blocked > 15 minutes in `NJ-DGE`.

## Regulatory note

NJ-DGE requires settlement reconciliation within the published SLA. Document incident start/end times for compliance audit.

## Related documents

- `runbook_kafka_consumer_lag.md` — settlement Kafka consumer lag (RB-009)
- `runbook_db_cpu.md`
- `incident_history.csv` — INC-2026-NJ-001
