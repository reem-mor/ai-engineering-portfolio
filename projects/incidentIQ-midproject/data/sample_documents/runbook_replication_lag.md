# RB-004: Runbook — Postgres replication lag > 30s (NJ-DGE)

**Runbook ID:** RB-004  
**Severity:** P2  
**Applies to:** PostgreSQL replicas in `NJ-DGE`, `GIB`, hosts matching `*-db-replica-*`  
**Alert:** `PostgresReplicationLag` / `PostgresReplicaLag` — replica lag > 30 seconds sustained 5 minutes

## Symptoms

- Grafana panel `postgres_replication_lag_seconds` above threshold on `nj-db-replica-01`.
- Read-after-write inconsistencies on reporting and settlement read paths.
- `pg_last_wal_replay_lsn` falling behind the primary.
- Primary CPU may be elevated (`PostgresCpuHigh` correlated).

## Detection checks

1. Measure current lag in seconds and bytes.
2. Check primary load and long-running write transactions.
3. Confirm network throughput between primary and replica.
4. Correlate with recent deploys or batch jobs.

## Detection SQL

```sql
-- On the replica
SELECT now() - pg_last_xact_replay_timestamp() AS replica_lag;
-- On the primary
SELECT client_addr, state, sent_lsn, replay_lsn,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;
```

## Recommended steps

1. Confirm lag on all replicas using the SQL above.
2. Check primary load — if CPU > 90%, follow `runbook_db_cpu.md` first.
3. If a heavy primary query is the cause, address it (RB-007).
4. Route read-after-write traffic to the primary temporarily.
5. Identify long-running transactions blocking replay on primary.
6. Verify network path between primary and replica (no firewall change in last deploy).
7. Pause non-critical batch writes until lag recovers.
8. If lag > 120s and customer-facing reads affected, consider read traffic shift to healthy replica.
9. If a replica cannot catch up, plan a reseed during a maintenance window.
10. Escalate to DBA on-call if lag does not decrease within 15 minutes.

## Dangerous actions warning

- Do NOT promote a lagging replica to primary — this risks data loss.
- Do NOT disable WAL archiving to "free" I/O.

## Escalation

- **Tier-1:** Steps 1–4 when lag < 60s and no write impact.
- **DBA on-call:** Lag > 120s, failover risk, replica cannot catch up, or cancel/terminate on primary required.
- **P1:** Settlement or auth blocked by stale reads in `NJ-DGE`.

## Regulatory note

Delayed replication can affect audit trail completeness for NJ gaming transactions. Log replica names and lag peaks.

## Related documents

- `runbook_db_cpu.md`
- `database_connectivity_runbook.md`
- `incident_history.csv` — INC-2026-NJ-002
