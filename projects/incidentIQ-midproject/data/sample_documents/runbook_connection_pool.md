# Runbook: Application connection pool exhausted (postgres / NJ-DGE)

**Severity:** P2  
**Applies to:** Services using Hikari/JDBC pools against `postgres` in `NJ-DGE`  
**Alert:** `ConnectionPoolExhausted` — active connections at pool max, wait time > 5s

## Symptoms

- Application logs: `HikariPool - Connection is not available, request timed out after 30000ms`.
- Postgres `pg_stat_activity` shows many connections in `idle in transaction`.
- Correlated with traffic spike or recent deploy changing pool size.

## Recommended steps

1. Identify service with exhausted pool (checkout, auth, settlement) from alert labels.
2. On Postgres: list connections by application name and state.
3. Terminate idle-in-transaction sessions older than 10 minutes (with app team approval).
4. Verify pool max size vs. Postgres `max_connections` — no single service should hold > 40% of max.
5. Check for connection leak in latest deploy; correlate with `correlate_deployments` tool.
6. Restart affected app pods only after DBA confirms no blocking DDL.

## Escalation

- **Tier-1:** Steps 1–4 when connections recover after idle cleanup.
- **App on-call + DBA:** Pool settings wrong after deploy or leak confirmed.
- **P1:** All writes failing (`postgres-primary` saturation).

## Regulatory note

Do not mass-terminate backends without documenting PIDs and owning services — required for post-incident review in regulated environments.

## Related documents

- `database_connectivity_runbook.md`
- `runbook_db_cpu.md`
- `incident_history.csv` — INC-2025-019, INC-2026-NJ-003
