---
title: "Postgres replica lag"
doc_type: "runbook"
services: ["postgres"]
environments: ["NJ-DGE", "GIB-UKGC"]
severity_applicable: ["P2", "P3"]
tags: ["postgres", "replication", "database"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-004: PostgreSQL Replica Lag

**Severity:** P2
**Applies to:** `postgres` read replicas in `NJ-DGE`, `GIB`
**Alert name:** `PostgresReplicaLag` — replica lag > 30s sustained for 5 minutes

## Symptoms

- Read-after-write inconsistencies on reporting and dashboards.
- `pg_last_wal_replay_lsn` falling behind the primary.
- Lag often follows a primary CPU spike (see RB-007) or a large write batch.

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

1. If a heavy primary query is the cause, address it (RB-007).
2. Route read-after-write traffic to the primary temporarily.
3. Pause non-critical batch writes until lag recovers.
4. If a replica cannot catch up, plan a reseed during a maintenance window.

## Dangerous actions warning

- Do NOT promote a lagging replica to primary — this risks data loss.
- Do NOT disable WAL archiving to "free" I/O.

## Escalation path

- **Tier-1:** Steps 1–3 when lag is recovering after reducing primary load.
- **dba-oncall:** Lag > 60s for 15 minutes or replica cannot catch up.
- **P1:** Stale reads affecting settlement or compliance reporting.

## Business / regulatory impact

Stale reads can show incorrect balances and reporting figures; in regulated
markets reporting accuracy is auditable.

## Tags / services

`postgres`, `replica`, `replication-lag`, `wal`, `read-after-write`, `dba`
