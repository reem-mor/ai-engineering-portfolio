---
title: "Promotions engine latency"
doc_type: "runbook"
services: ["promotions-engine", "checkout-api"]
environments: ["NJ-DGE", "GIB-UKGC"]
severity_applicable: ["P2", "P3"]
tags: ["promotions", "latency", "checkout"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-006: Promotions Engine Latency

**Severity:** P2 (P3 if non-blocking)
**Applies to:** `promotions-engine` feeding `checkout-api` in `NJ-DGE`, `GIB`
**Alert name:** `PromotionsLatencyHigh` — promo evaluation p95 > 800ms over 5 minutes

## Symptoms

- Checkout slows when applying bonuses/promotions.
- Promotions engine p95 latency rises; cache hit ratio drops.
- Increased calls to `postgres` for promo rules (cache miss storm).

## Detection checks

1. Check promotions-engine cache hit ratio and `redis-cache` health (RB-008).
2. Inspect slow promo-rule queries against `postgres`.
3. Correlate with a recent promo-rules deploy via `correlate_deployments`.
4. Confirm whether one campaign with a heavy rule set is the hotspot.

## Recommended steps

1. If cache is cold or evicting, warm it and verify `redis-cache` (RB-008).
2. Disable or throttle the single heavy campaign rather than all promotions.
3. If a deploy regressed rule evaluation, roll back (RB-010).
4. Add the missing index if a promo query does a sequential scan.

## Dangerous actions warning

- Do NOT disable all promotions globally if one campaign is the cause —
  this has direct revenue and player-trust impact.

## Escalation path

- **Tier-1:** Steps 1–2 when latency recovers after cache warm-up.
- **checkout-oncall:** p95 > 800ms for 15 minutes affecting checkout.
- **P2 -> P1:** If promo latency starts failing checkout transactions.

## Business / regulatory impact

Promotion failures reduce conversion and can mis-apply regulated bonus terms;
bonus terms in some markets are subject to compliance rules.

## Example commands

```sql
-- Slowest promo-rule queries
SELECT query, mean_exec_time, calls FROM pg_stat_statements
WHERE query ILIKE '%promo_rule%' ORDER BY mean_exec_time DESC LIMIT 10;
```

## Tags / services

`promotions-engine`, `checkout-api`, `redis-cache`, `latency`, `cache`, `postgres`
