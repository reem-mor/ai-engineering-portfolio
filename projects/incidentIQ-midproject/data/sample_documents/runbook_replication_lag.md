# Runbook: Postgres replication lag > 30s (NJ-DGE)

**Severity:** P2  
**Applies to:** PostgreSQL replicas in `NJ-DGE`, hosts matching `*-db-replica-*`  
**Alert:** `PostgresReplicationLag` — replica lag > 30 seconds sustained 5 minutes

## Symptoms

- Grafana panel `postgres_replication_lag_seconds` above threshold on `nj-db-replica-01`.
- Read-after-write inconsistencies on reporting and settlement read paths.
- Primary CPU may be elevated (`PostgresCpuHigh` correlated).

## Recommended steps

1. Confirm lag on all replicas: `SELECT application_name, state, sync_state, replay_lag FROM pg_stat_replication;`
2. Check primary load — if CPU > 90%, follow `runbook_db_cpu.md` first.
3. Identify long-running transactions blocking replay on primary.
4. Verify network path between primary and replica (no firewall change in last deploy).
5. If lag > 120s and customer-facing reads affected, consider read traffic shift to healthy replica.
6. Escalate to DBA on-call if lag does not decrease within 15 minutes.

## Escalation

- **Tier-1:** Steps 1–4 when lag < 60s and no write impact.
- **DBA on-call:** Lag > 120s, failover risk, or cancel/terminate on primary required.
- **P1:** Settlement or auth blocked by stale reads in `NJ-DGE`.

## Regulatory note

Delayed replication can affect audit trail completeness for NJ gaming transactions. Log replica names and lag peaks.

## Related documents

- `runbook_db_cpu.md`
- `database_connectivity_runbook.md`
- `incident_history.csv` — INC-2026-NJ-002
