---
title: "Redis token store degradation"
doc_type: "runbook"
services: ["redis-cache", "auth-api"]
environments: ["NJ-DGE", "GIB-UKGC", "MGM"]
severity_applicable: ["P1", "P2"]
tags: ["redis", "auth", "cache"]
last_updated: "2026-06-07"
author: "PITER AiOps"
version: "1.0"
---

# RB-008: Redis / Token-Store Degradation

**Severity:** P1 (auth impact) / P2 (cache only)
**Applies to:** `redis-cache` backing `auth-api` token store and promo cache
**Alert name:** `RedisDegraded` — eviction storm, OOM, or failover incomplete

## Symptoms

- Sessions expiring early or being invalidated.
- `auth-api` login errors rise (token store unavailable — see RB-002).
- Redis master OOM, eviction rate spiking, or an incomplete failover.

## Detection checks

1. Check Redis memory usage, eviction policy, and evicted-keys rate.
2. Confirm master/replica roles and whether a failover completed.
3. Identify large keys or a key-space spike from a deploy.
4. Verify `auth-api` and `promotions-engine` dependency health.

## Recommended steps

1. If eviction storm: confirm `maxmemory-policy` and reduce key churn source.
2. If master OOM and failover incomplete, complete failover to a healthy replica.
3. Warm critical caches after recovery (token store first, then promos).
4. If a deploy caused unbounded key growth, roll it back (RB-010).

## Dangerous actions warning

- Do NOT run `FLUSHALL`/`FLUSHDB` on the token store — it logs out every user.
- Do NOT force failover without confirming replica data freshness.

## Escalation path

- **Tier-1:** Steps 1 and 3 when cache recovers without auth impact.
- **platform-oncall + identity-oncall:** Auth login impact or failed failover.
- **P1:** Token store down → user logins failing.

## Business / regulatory impact

Token-store loss logs out all players and blocks authenticated play; mass
session invalidation is a customer-impact event.

## Example commands

```bash
redis-cli info memory | grep -E 'used_memory_human|maxmemory_human|evicted_keys'
redis-cli info replication | grep -E 'role|master_link_status'
```

## Tags / services

`redis-cache`, `token-store`, `auth-api`, `eviction`, `failover`, `cache`
