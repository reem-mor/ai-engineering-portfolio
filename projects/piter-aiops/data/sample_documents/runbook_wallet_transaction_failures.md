---
title: "Wallet transaction failures"
doc_type: "runbook"
services: ["wallet-service"]
environments: ["GIB-UKGC", "NJ-DGE", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3"]
tags: ["wallet", "transactions", "balance", "tier-0"]
last_updated: "2026-06-08"
author: "PITER AiOps"
version: "1.0"
---

# RB-012: Wallet Transaction Failures

## When to use

Use when wallet balance queries, deposits, withdrawals, or internal wallet transfers fail or time out. Downstream impact often surfaces as `bet-service` or `payments-service` errors due to retry storms.

## Severity guidance

| Condition | Priority |
|-----------|----------|
| All wallet operations failing in regulated market | **P1** |
| Deposit/withdrawal blocked, balance reads OK | **P2** |
| Elevated latency, partial transaction failures | **P3** |
| Single-provider timeout with fallback active | **P4** |

## Prerequisites

- Grafana: `grafana://piter/wallet-service`
- On-call: Primary/Secondary Wallet Platform On-Call (`#wallet-platform`)
- Access to `payments-service` and `replication` dependency dashboards

## Investigation steps

1. Identify failure mode: balance read, debit/credit, deposit, or withdrawal path.
2. Check recent deploys for wallet-service and payments-service in the same environment.
3. Inspect database replication lag (wallet uses `replication` for consistency).
4. Review connection pool and slow-query metrics on transaction stores.
5. Check auth-service token validation latency (wallet depends on session validity).
6. Look for retry storms from bet-service or payments-service callers.

## Triage decision tree

```
Wallet transaction failures?
├─ Deploy within lookback window? → Suspect config or schema change (rollback candidate)
├─ Replication lag > 60s? → Data platform path (RB-004)
├─ payments-service degraded? → Fix payment routing first
├─ Pool pressure + high caller retries? → Throttle retries, restart pool
└─ Provider timeout only? → Failover to secondary payment route
```

## Remediation

1. Throttle or circuit-break upstream callers if retry storm detected.
2. Roll back suspect wallet deployment if correlated with onset (RB-010).
3. Scale wallet workers only after replication and payments paths are healthy.
4. Clear stuck transaction queue after DBA approval.
5. Re-enable traffic gradually with canary wallet operations.

## Verification

1. Sample deposit, withdrawal, and balance read succeed in affected environment.
2. Transaction error rate below 0.5% for 10 minutes.
3. No growing dead-letter queue on wallet events.
4. Dependent services (bet-service) show recovered error rates.

## Rollback

Follow **RB-010**. Use `rollback_version` from the suspect `wallet-service` deploy. Validate ledger consistency before full traffic restore.

## Escalation

- **Primary Wallet Platform On-Call:** P1/P2 wallet unavailability.
- **Data Platform On-Call:** Replication or ledger inconsistency suspected.
- **Payments On-Call:** Provider routing failure upstream.
- Do not store real phone numbers or personal email addresses in incident notes.

## Related

- RB-004 Postgres replica lag
- RB-005 Connection pool exhaustion
- RB-010 Deployment rollback
- RB-013 Payment provider degradation
