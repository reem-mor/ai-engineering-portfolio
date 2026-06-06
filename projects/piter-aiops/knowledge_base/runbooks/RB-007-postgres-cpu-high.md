---
title: "Postgres CPU high"
doc_type: "runbook"
services: ["postgres"]
environments: ["NJ-DGE", "GIB-UKGC", "MGM"]
severity_applicable: ["P1", "P2"]
tags: ["postgres", "cpu", "database"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-007: PostgreSQL CPU Above 90%

**Severity:** P2 (P1 if checkout/auth blocked)
**Applies to:** `postgres` primary hosts matching `prod-db-*` in `NJ-DGE`, `GIB`, `MGM`
**Alert name:** `PostgresCpuHigh` — CPU > 90% sustained for 5 minutes

## Symptoms

- Sustained CPU above 90% on a `postgres` primary (e.g. `prod-db-1`).
- Query latency rises across dependent services (settlement, checkout, auth).
- Often driven by a long-running analytics query or a missing index after a deploy.

## Detection checks

1. Confirm the alert and the affected host/environment.
2. Connect through the bastion host to the affected primary.
3. Identify long-running queries in `pg_stat_activity`.
4. Check for missing indexes (high `seq_scan` vs `idx_scan`).
5. Correlate with recent deploys using `correlate_deployments`.

## Detection / remediation SQL

```sql
-- 1. Find active long-running queries
SELECT pid, usename, state, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- 2. Cancel queries running longer than 5 minutes
SELECT pg_cancel_backend(pid) FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 minutes';

-- 3. Terminate the backend ONLY if cancel fails
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid = <pid>;
```

## Recommended steps

1. Confirm the alert and identify long-running queries (SQL step 1).
2. Cancel queries running longer than 5 minutes (SQL step 2).
3. Terminate the backend only if cancel fails (SQL step 3).
4. Check for missing indexes using `pg_stat_user_tables`.
5. If load persists, fail over to the replica using Patroni (`patronictl failover`).
6. Escalate to DBA on-call if CPU remains above 90% for 15 minutes.

## Dangerous actions warning

- `pg_terminate_backend` forcibly kills a session and can roll back in-flight
  work — use only after `pg_cancel_backend` fails, and record the PID.
- Do NOT run a Patroni failover during active settlement without payments sign-off.

## Escalation path

- **Tier-1:** Steps 1–4 when the runbook applies and there is no data-loss risk.
- **dba-oncall:** CPU > 90% for 15 minutes, failover required, or cancel/terminate ineffective.
- **P1:** Customer-facing checkout or auth blocked by database saturation.

## Business / regulatory impact

`postgres` is the system of record. Sustained saturation in `NJ-DGE` delays
settlement and blocks play; P2 here carries SLA and regulatory exposure.

## Tags / services

`postgres`, `cpu`, `pg_stat_activity`, `patroni`, `failover`, `dba`, `prod-db-1`
