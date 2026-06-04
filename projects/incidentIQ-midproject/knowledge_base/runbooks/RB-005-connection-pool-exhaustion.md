# RB-005: Connection Pool Exhaustion

**Severity:** P2 (P1 if all writes fail)
**Applies to:** Services using Hikari/JDBC pools against `postgres` in `NJ-DGE`
**Alert name:** `ConnectionPoolExhausted` — active connections at pool max, wait > 5s

## Symptoms

- App logs: `HikariPool - Connection is not available, request timed out after 30000ms`.
- `postgres` `pg_stat_activity` shows many `idle in transaction` sessions.
- Often correlated with a traffic spike or a deploy that changed pool size.

## Detection checks

1. Identify which service (checkout, auth, settlement) exhausted its pool.
2. List connections by application name and state.
3. Compare pool max vs. `postgres` `max_connections` (no service > 40% of max).
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

1. Terminate idle-in-transaction sessions older than 10 minutes (with app-team approval).
2. Verify and correct pool max if a deploy changed it.
3. If a connection leak is confirmed in the latest deploy, roll back (RB-010).
4. Restart affected app pods only after DBA confirms no blocking DDL.

## Dangerous actions warning

- Do NOT mass-terminate backends without recording PIDs and owning services —
  this is required for post-incident review in regulated environments.
- Do NOT raise `max_connections` blindly; it can OOM the database.

## Escalation path

- **Tier-1:** Steps 1–2 when connections recover after idle cleanup.
- **dba-oncall + app on-call:** Pool wrong after deploy or leak confirmed.
- **P1:** All writes failing due to `postgres` saturation.

## Business / regulatory impact

Write failures block deposits, bets, and settlement. Document all terminated
sessions for the post-incident record.

## Tags / services

`postgres`, `connection-pool`, `hikari`, `idle-in-transaction`, `deploy`, `dba`
