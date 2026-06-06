---
title: "Kafka consumer lag"
doc_type: "runbook"
services: ["settlement-svc", "kafka-settlement"]
environments: ["NJ-DGE", "GIB-UKGC"]
severity_applicable: ["P1", "P2"]
tags: ["kafka", "consumer-lag", "settlement"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-009: Kafka Consumer Lag

**Severity:** P2 (P1 if settlement consumer)
**Applies to:** Kafka consumer groups feeding `settlement-svc` and analytics in `NJ-DGE`
**Alert name:** `KafkaConsumerLag` — consumer group lag > 100k messages or rising 10 min

## Symptoms

- Consumer group lag growing on a partition or across the group.
- Downstream processing (settlement, analytics) falling behind real time.
- Often follows a slow consumer deploy, a rebalance storm, or a poison message.

## Detection checks

1. Identify the lagging consumer group and partitions.
2. Check whether consumers are healthy or stuck in a rebalance loop.
3. Look for a poison/oversized message blocking a partition.
4. Correlate with the latest consumer deploy via `correlate_deployments`.

## Recommended steps

1. If consumers are under-scaled, add consumer instances (up to partition count).
2. If a rebalance storm, stabilize membership (check session/heartbeat timeouts).
3. If a poison message blocks a partition, quarantine it to a dead-letter topic.
4. If a deploy regressed processing throughput, roll back (RB-010).

## Dangerous actions warning

- Do NOT reset consumer offsets to `latest` to "clear" lag on the settlement
  group — this skips unprocessed financial events.
- Do NOT delete a topic to clear a backlog.

## Escalation path

- **Tier-1:** Steps 1–2 when lag recovers after scaling.
- **platform-oncall:** Lag rising > 15 minutes or rebalance loop persists.
- **P1:** Settlement consumer lag delaying money movement → payments-oncall.

## Business / regulatory impact

Settlement-stream lag delays money movement and reporting; offset resets on
financial topics can drop auditable events.

## Example commands

```bash
kafka-consumer-groups --bootstrap-server $BROKER --describe --group settlement-consumer
```

## Tags / services

`kafka`, `consumer-lag`, `settlement-svc`, `rebalance`, `dead-letter`, `offsets`
