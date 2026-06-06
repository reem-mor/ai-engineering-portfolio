---
title: "Settlement backlog"
doc_type: "runbook"
services: ["settlement-svc"]
environments: ["NJ-DGE", "GIB-UKGC"]
severity_applicable: ["P1", "P2"]
tags: ["settlement", "kafka", "payments"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-003: Settlement Backlog / Payment Errors

**Severity:** P1
**Applies to:** `settlement-svc` in `NJ-DGE`, `GIB`
**Alert name:** `SettlementBacklogGrowing` — pending settlements queue depth rising > 10 min

## Symptoms

- `settlement-svc` queue depth climbing; settlement latency past SLA.
- Payment confirmations delayed; charges retried via backup PSP.
- Errors reference `postgres` write contention or PSP timeouts.

## Detection checks

1. Check `settlement-svc` dependency health: `postgres` and `payment-svc`.
2. Inspect PSP error rate and timeout metrics.
3. Correlate recent `settlement-svc` deploys with `correlate_deployments`.
4. Verify `postgres` is not saturated (see RB-007) — settlement depends on it.

## Recommended steps

1. If `postgres` is the bottleneck, resolve DB saturation first (RB-007 / RB-005).
2. If primary PSP is timing out, confirm failover to backup PSP is active.
3. Drain the backlog gradually; do not replay duplicate settlements.
4. Reconcile settled vs. pending counts before declaring recovery.

## Dangerous actions warning

- Do NOT blindly replay the settlement queue — duplicate settlements double-charge
  customers and create a regulatory finance incident.
- Do NOT disable idempotency keys to "speed up" draining.

## Escalation path

- **Tier-1:** Steps 1–2 when the cause is an upstream dependency already covered.
- **payments-oncall:** Backlog growing > 15 minutes or reconciliation mismatch.
- **P1:** Customer funds affected → page `payments-l2 -> payments-oncall`.

## Business / regulatory impact

Settlement is money-movement. Delays and duplicates are regulated-finance events
with direct revenue and compliance exposure; document all queue actions.

## Example commands

```sql
-- Pending settlement depth and age
SELECT status, count(*), max(now() - created_at) AS oldest
FROM settlements WHERE status = 'pending' GROUP BY status;
```

## Tags / services

`settlement-svc`, `payments`, `psp`, `postgres`, `backlog`, `reconciliation`
