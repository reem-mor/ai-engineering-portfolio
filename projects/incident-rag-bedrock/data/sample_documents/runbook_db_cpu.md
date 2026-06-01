# Runbook: Postgres CPU above 90% on prod-db-* hosts

**Severity:** P2  
**Applies to:** PostgreSQL primary hosts matching `prod-db-*`  
**Alert:** `PostgresCpuHigh` — CPU > 90% sustained for 5 minutes

## Recommended steps

1. Confirm the alert and identify long-running queries.
2. Connect through the bastion host to the affected primary.
3. Run the following against `pg_stat_activity`:

```sql
SELECT pid, usename, state, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;
```

4. Cancel queries running longer than 5 minutes:

```sql
SELECT pg_cancel_backend(pid) FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 minutes';
```

5. Terminate the backend only if cancel fails:

```sql
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE pid = <pid>;
```

6. Check for missing indexes using `pg_stat_user_tables` (high `seq_scan` vs `idx_scan`).
7. If load persists, fail over to the replica using Patroni (`patronictl failover`).
8. Escalate to DBA on-call if CPU remains above 90% for 15 minutes.

## Escalation

- **Tier-1:** Steps 1–6 when the runbook applies and no data-loss risk.
- **DBA on-call:** CPU > 90% for 15 minutes, failover required, or cancel/terminate ineffective.
- **P1:** Customer-facing checkout or auth blocked by database saturation.

## Related documents

- `database_connectivity_runbook.md` — connection pool and replica checks
- `alerts_last_3mo.json` — alert A-1108 (prod-db-1 CPU incident)
