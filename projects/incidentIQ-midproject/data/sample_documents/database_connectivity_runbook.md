# Database Connectivity Runbook

Applies to: PostgreSQL primary + replicas, Redis session/cache layer.

## Symptoms that map here

- Applications log `connection refused`, `too many connections`, or
  `SSL handshake failed`
- p95 query latency above 1 second sustained for 5 minutes
- Replication lag above 30 seconds on any read replica
- `idle in transaction` connections above 50

## Postgres — fast checks

```bash
# From a bastion host
psql -h prod-pg-primary.example.com -U readonly -c \
  "SELECT count(*) FROM pg_stat_activity WHERE state='active';"
psql ... -c "SELECT now() - pg_last_xact_replay_timestamp() AS lag;"
```

If active connections are above 80% of `max_connections`, the application
is leaking. Restart the offending app pod fleet **before** touching the
database. Killing Postgres backends only buys a few seconds.

## Redis — fast checks

```bash
redis-cli -h prod-redis.example.com PING
redis-cli -h prod-redis.example.com INFO replication | head
redis-cli -h prod-redis.example.com INFO memory | grep used_memory_human
```

If `used_memory_human` is within 90% of the maxmemory cap, evictions
will start failing session writes — see auth runbook.

## When the database is the actual cause

- **Locks:** `SELECT * FROM pg_locks WHERE NOT granted;` — kill the
  oldest blocking PID only with DBA on the call.
- **Replica lag:** if a read replica is more than 5 minutes behind, take
  it out of rotation in the load balancer.
- **Disk full:** `df -h /var/lib/postgresql` — if above 90%, immediately
  truncate the `audit_log` table after exporting; this needs the DBA.

## Do NOT

- Do **not** run `FLUSHDB` against Redis without on-call lead approval.
- Do **not** restart Postgres during business hours without a documented
  recovery window — failover takes ~3 minutes and drops in-flight
  transactions.
