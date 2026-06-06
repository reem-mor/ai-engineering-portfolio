# RB-005: Runbook — Application connection pool exhausted (postgres / NJ-DGE)

**Runbook ID:** RB-005  
**Severity:** P2 (P1 if all writes fail)  
**Applies to:** Services using Hikari/JDBC pools against `postgres` in `NJ-DGE`  
**Alert:** `ConnectionPoolExhausted` — active connections at pool max, wait time > 5s

## Symptoms

- Application logs: `HikariPool - Connection is not available, request timed out after 30000ms`.
- Postgres `pg_stat_activity` shows many connections in `idle in transaction`.
- Often correlated with a traffic spike or a deploy that changed pool size.

## Detection checks

1. Identify service with exhausted pool (checkout, auth, settlement) from alert labels.
2. List connections by application name and state.
3. Compare pool max vs. Postgres `max_connections` — no single service should hold > 40% of max.
4. Correlate with the latest deploy via `correlate_deployments` (connection leak).

## Detection SQL

```sql
SELECT application_name, state, count(*)
FROM pg_stat_activity GROUP BY 1, 2 ORDER BY 3 DESC;

-- Idle-in-transaction sessions older than 10 minutes
SELECT pid, application_name, now() - state_change AS idle_for
FROM pg_stat_activity
WHERE state = 'idle in transaction' AND now() - state_change > interval '10 minutes';
```

## Recommended steps

1. On Postgres: list connections by application name and state.
2. Terminate idle-in-transaction sessions older than 10 minutes (with app team approval).
3. Verify pool max size vs. Postgres `max_connections`.
4. If a connection leak is confirmed in the latest deploy, roll back (`runbook_deployment_rollback.md`).
5. Restart affected app pods only after DBA confirms no blocking DDL.

## Dangerous actions warning

- Do NOT mass-terminate backends without recording PIDs and owning services —
  this is required for post-incident review in regulated environments.
- Do NOT raise `max_connections` blindly; it can OOM the database.

## Escalation

- **Tier-1:** Steps 1–3 when connections recover after idle cleanup.
- **App on-call + DBA:** Pool settings wrong after deploy or leak confirmed.
- **P1:** All writes failing (`postgres-primary` saturation).

## Regulatory note

Write failures block deposits, bets, and settlement. Document all terminated
sessions for the post-incident record.

## Related documents

- `database_connectivity_runbook.md`
- `runbook_db_cpu.md`
- `incident_history.csv` — INC-2025-019, INC-2026-NJ-003
