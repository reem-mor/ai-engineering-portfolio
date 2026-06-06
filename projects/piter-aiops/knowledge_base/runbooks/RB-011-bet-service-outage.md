---
title: "Bet service outage and error rate spike"
doc_type: "runbook"
services: ["bet-service", "bet-api", "kafka-settlement"]
environments: ["GIB-UKGC", "NJ-DGE", "MGM"]
severity_applicable: ["P1", "P2"]
tags: ["betting", "error-rate", "regulated-market", "demo-p1"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-011: Bet Service Outage and Error Rate Spike

**Severity:** P1 (100% error rate) / P2 (partial degradation)
**Applies to:** `bet-service` and `bet-api` in regulated markets (`GIB-UKGC`, `NJ-DGE`)
**Alert name:** `BetServiceErrorRateHigh` — error rate > 5% over 2 minutes; demo trigger at 100%

## Symptoms

- Customer-facing betting APIs return 5xx or time out.
- Edge dashboards show 100% error rate on `bet-service` in `GIB-UKGC`.
- Warning shots may precede the P1: memory pressure, Kafka lag, or connection pool warnings.

## Detection checks

1. Confirm scope: environment, market, and whether wallet/settlement paths are affected.
2. Check recent deployments with the `correlate_deployments` tool.
3. Inspect dependency health: `postgres`, `kafka-settlement`, and downstream wallet APIs.
4. Review circuit breaker and rate-limit state on `bet-api`.
5. Compare error rate with synthetic canary traffic.

## Recommended steps

1. Declare P1 if regulated-market betting is unavailable or error rate exceeds 50% for 5 minutes.
2. Roll back suspect deployment if correlation window matches alert onset (see RB-010).
3. Validate database connection pool and active sessions on `postgres`.
4. Check Kafka consumer lag for settlement topics (see RB-009).
5. Scale `bet-service` only after ruling out bad deploy or dependency saturation.
6. Monitor error rate and settlement backlog for 10 minutes after mitigation.

## Escalation path

- **Tier-1:** Initial triage and dependency checks.
- **betting-oncall:** Sustained P1 in any regulated market.
- **P1:** GIB-UKGC or NJ-DGE betting unavailable → page `betting-l2 -> betting-oncall`.

## Business / regulatory impact

- Direct revenue loss during peak betting windows.
- UKGC and state regulator reporting may be required for prolonged outages.
- Do not store real phone numbers or personal email addresses in incident notes.

## Related runbooks

- RB-005 Connection pool exhaustion
- RB-009 Kafka consumer lag
- RB-010 Deployment rollback
