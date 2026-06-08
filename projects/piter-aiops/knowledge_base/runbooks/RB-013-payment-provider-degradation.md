---
title: "Payment provider degradation"
doc_type: "runbook"
services: ["payments-service"]
environments: ["GIB-UKGC", "NJ-DGE", "MGM", "MIRAGE"]
severity_applicable: ["P1", "P2", "P3"]
tags: ["payments", "provider", "pci", "authorization"]
last_updated: "2026-06-08"
author: "Re'em Mor"
version: "1.0"
---

# RB-013: Payment Provider Degradation

## When to use

Use when payment authorization latency exceeds SLO, provider timeouts increase, or routing to external payment gateways fails. Affects deposits and cash-out flows; may cascade to wallet-service retries.

## Severity guidance

| Condition | Priority |
|-----------|----------|
| All payment providers unreachable in regulated market | **P1** |
| Primary provider down, failover degraded | **P2** |
| Latency > 3s p95, success rate > 95% | **P3** |
| Single region provider slowness with workaround | **P4** |

PCI-DSS scope: do not log full card data in incident channels.

## Prerequisites

- Grafana: `grafana://piter/payments-service`
- On-call: Primary/Secondary Payments On-Call (`#payments`)
- Provider status page access (sanitized demo: internal status dashboard)

## Investigation steps

1. Map affected payment methods and environments.
2. Correlate recent payments-service deploys.
3. Check external provider health and timeout histograms per route.
4. Inspect wallet-service callback success rate (downstream dependency).
5. Review circuit breaker state per provider adapter.
6. Confirm no certificate or credential rotation in last 24 hours (use Secrets Manager workflow — never paste secrets in tickets).

## Triage decision tree

```
Payment degradation?
├─ External provider outage confirmed? → Enable failover route, notify provider liaison
├─ Deploy correlated? → Rollback payments-service (RB-010)
├─ wallet-service callbacks failing? → Fix wallet path first
├─ Timeout spike, provider healthy? → Check connection pool and thread exhaustion
└─ Single method affected? → Disable method flag, route to alternate
```

## Remediation

1. Switch to secondary provider route when primary exceeds error budget.
2. Roll back suspect deployment if change introduced routing regression.
3. Increase provider timeout temporarily only with Payments lead approval.
4. Drain stuck authorization queue after verifying idempotency keys.
5. Communicate customer-facing status via approved channels only.

## Verification

1. Authorization success rate above 99% for 15 minutes on affected routes.
2. p95 latency below 2 seconds on primary provider.
3. Wallet deposit/withdrawal end-to-end test passes.
4. No duplicate charges in reconciliation sample.

## Rollback

Follow **RB-010** for payments-service deploys. Provider-side changes require provider console rollback per change ticket — do not modify production routing without Payments lead.

## Escalation

- **Primary Payments On-Call:** P1/P2 payment outage.
- **PCI incident path:** If cardholder data exposure suspected, invoke security incident process (mock mode in demo).
- **Wallet Platform:** If wallet callbacks are root cause, not provider.
- Do not store real phone numbers or personal email addresses in incident notes.

## Related

- RB-010 Deployment rollback
- RB-012 Wallet transaction failures
- POL-001 Severity and escalation policy
