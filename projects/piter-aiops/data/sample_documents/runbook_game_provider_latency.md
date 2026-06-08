---
title: "Game provider latency"
doc_type: "runbook"
services: ["game-service"]
environments: ["GIB-UKGC", "NJ-DGE", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3", "P4"]
tags: ["game", "provider", "latency", "session"]
last_updated: "2026-06-08"
author: "PITER AiOps"
version: "1.0"
---

# RB-014: Game Provider Latency

## When to use

Use when game launch latency spikes, provider handoff timeouts occur, or game session routing fails. Tier-1 service — customer-facing but typically lower revenue impact than bet-service or wallet outages.

## Severity guidance

| Condition | Priority |
|-----------|----------|
| All game launches failing in regulated market | **P2** (P1 if combined with bet outage) |
| p95 launch latency > 5s for 10+ minutes | **P3** |
| Single provider degraded, others healthy | **P4** |
| Capacity warning only | **P4** |

## Prerequisites

- Grafana: `grafana://piter/game-service`
- On-call: Primary/Secondary Game Platform On-Call (`#game-platform`)
- auth-service and wallet-service health visibility

## Investigation steps

1. Identify affected game providers and environments.
2. Correlate recent game-service deploys.
3. Check auth-service session validation latency (launch depends on valid token).
4. Check wallet-service balance pre-check latency for real-money games.
5. Review provider API latency and error codes by vendor.
6. Inspect CDN or edge cache hit rates for game assets.

## Triage decision tree

```
Game launch latency?
├─ auth-service degraded? → Fix identity path (RB-002)
├─ wallet pre-check slow? → Wallet path (RB-012)
├─ Deploy correlated? → Rollback game-service (RB-010)
├─ Single provider slow? → Drain traffic from provider, notify vendor
└─ Asset CDN miss spike? → Warm cache or failover CDN origin
```

## Remediation

1. Disable feature flag for affected provider integration if partial outage.
2. Roll back suspect game-service deployment when correlated.
3. Increase provider timeout budget only with Game Platform lead approval.
4. Scale game-session routers after dependencies are healthy.
5. Warm CDN cache for top titles if asset latency is root cause.

## Verification

1. Game launch p95 below 2 seconds for 15 minutes.
2. Session handoff success rate above 99%.
3. No elevated 5xx on game launch API.
4. Sample launches across top 3 providers succeed.

## Rollback

Follow **RB-010** for game-service. Provider-side configuration rollback via vendor change ticket.

## Escalation

- **Primary Game Platform On-Call:** sustained P2/P3 game degradation.
- **Identity & Access:** auth/token failures blocking launch.
- **Wallet Platform:** balance pre-check blocking real-money games.
- Do not store real phone numbers or personal email addresses in incident notes.

## Related

- RB-002 Auth login failures
- RB-010 Deployment rollback
- RB-012 Wallet transaction failures
