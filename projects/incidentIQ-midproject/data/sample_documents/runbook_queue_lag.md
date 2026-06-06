# Runbook: Email / worker queue lag (not Kafka)

**Note:** This runbook covers **email-worker / generic message queue** lag.
For **Kafka settlement consumer lag**, use `runbook_kafka_consumer_lag.md` (RB-009).

**Severity:** P3 (P2 if lag > 2 minutes or DLQ growing)  
**Service:** email-worker / message queue consumers  
**Alert:** `QueueLagHigh` — consumer lag > 30s for 5m

## Recommended steps

1. Check worker health — pod status, restarts, OOM kills in the worker namespace.
2. Check queue depth — compare current depth to baseline for this time of day.
3. Check recent deploys — new worker version may have slower handlers or bad config.
4. Scale workers if allowed — increase replica count within autoscaling limits.
5. Inspect dead-letter queue — failed messages may block progress or indicate poison pills.
6. Escalate if lag keeps increasing after scale-up or DLQ rate is abnormal.

## Escalation

- **Tier-1:** Scale workers and replay DLQ when runbook steps are deterministic.
- **Platform / messaging team:** Broker issues, partition rebalancing, sustained lag > 5 minutes.
- **P2:** Customer-visible email or notification delays beyond SLA.

## Related documents

- `runbook_kafka_consumer_lag.md` — Kafka consumer groups (settlement stream)
- `alerts_last_3mo.json` — alert A-1199 (email-worker lag)
- `monitoring_alerts_reference.md` — severity routing
