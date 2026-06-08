---
title: "Bet service outage and error rate spike"
doc_type: "runbook"
services: ["bet-service", "bet-api", "kafka-settlement"]
environments: ["GIB-UKGC", "NJ-DGE", "MGM"]
severity_applicable: ["P1", "P2"]
tags: ["betting", "error-rate", "regulated-market", "demo-p1"]
last_updated: "2026-06-08"
author: "Re'em Mor"
version: "2.0"
---

# RB-011: Bet Service Outage and Error Rate Spike

## When to use

Use this runbook when `bet-service` or `bet-api` reports elevated 5xx rates, node unresponsiveness, or complete betting unavailability in a regulated market (`GIB-UKGC`, `NJ-DGE`, `MGM`). Typical alerts: `BetServiceErrorRateHigh`, `service_down`, connection pool exhaustion preceding outage.

## Severity guidance

| Condition | Priority |
|-----------|----------|
| 100% error rate or nodes unresponsive in regulated market | **P1** — 5-minute response |
| Error rate > 50% for 5+ minutes | **P1** |
| Error rate 5–50% with degraded bet placement | **P2** — 15-minute response |
| Latency spike only, bets still succeeding | **P3** |

Align with `priority_matrix.json`: P1 when customer impact ≥ 20%, revenue risk ≥ $5,000/min, or UKGC/DGE reporting exposure.

## Prerequisites

- Grafana dashboard: `grafana://piter/bet-service`
- Deployment correlation for service/environment within 6 hours of alert
- On-call roles: Primary/Secondary Betting Core On-Call (`#betting-core`)
- Read access to wallet-service and postgres dependency dashboards

## Investigation steps

1. Confirm scope: environment, market, affected user count, and error rate percentage.
2. Correlate recent deployments for `bet-service` and dependencies (`wallet-service`, `auth-service`, `game-service`, `replication`).
3. Inspect connection pool utilization and circuit breaker state on `bet-api`.
4. Check wallet-service latency and retry fan-out (common root cause of pool saturation).
5. Review Kafka consumer lag on settlement topics (RB-009).
6. Compare synthetic canary bet placement success rate against production traffic.

## Triage decision tree

```
Error rate spike on bet-service?
├─ Deploy within 30 min of onset? → Suspect deployment (RB-010 rollback path)
├─ Connection pool > 90% + wallet retries elevated? → Pool exhaustion (RB-005)
├─ wallet-service or auth-service degraded? → Dependency failure — fix upstream first
└─ No deploy, pools healthy → Check kafka-settlement lag and postgres saturation
```

## Remediation

1. Declare P1 if regulated-market betting is unavailable or error rate exceeds 50%.
2. If deploy-correlated: initiate rollback per RB-010 using `rollback_version` from deploy record.
3. If pool exhaustion: disable retry fan-out, restart bet-service pool, validate wallet latency.
4. If dependency failure: coordinate with wallet/auth on-call before scaling bet-service.
5. Scale `bet-service` only after ruling out bad deploy or dependency saturation.
6. Monitor error rate and settlement backlog for 10 minutes after mitigation.

## Verification

1. Error rate below 1% for 5 consecutive minutes on affected environment.
2. Synthetic canary bet placement succeeds end-to-end.
3. Settlement backlog not growing (Kafka lag stable).
4. Connection pool utilization below 70% under current load.

## Rollback

Follow **RB-010 Deployment rollback**. Use the suspect deployment's `rollback_version` from `deploys.csv`. Confirm health checks pass before closing incident. Do not rollback without identifying change summary correlation.

## Escalation

- **Tier-1:** Initial triage and dependency checks (first 5 minutes).
- **Primary Betting Core On-Call:** Sustained P1 in any regulated market.
- **GIB-UKGC P1:** Page compliance officer role; UKGC reporting window 1 hour per escalation policy.
- Do not store real phone numbers or personal email addresses in incident notes.

## Related

- RB-005 Connection pool exhaustion
- RB-009 Kafka consumer lag
- RB-010 Deployment rollback
- POL-001 Severity and escalation policy
