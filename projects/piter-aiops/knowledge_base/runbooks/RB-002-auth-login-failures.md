---
title: "Authentication login failures"
doc_type: "runbook"
services: ["auth-api"]
environments: ["NJ-DGE", "GIB-UKGC", "MGM"]
severity_applicable: ["P1", "P2"]
tags: ["auth", "login", "identity"]
last_updated: "2026-06-07"
author: "Re'em Mor"
version: "1.0"
---

# RB-002: Authentication Login Failures

**Severity:** P1 (all users) / P2 (subset)
**Applies to:** `auth-api` in `NJ-DGE`, `GIB`, `MGM`
**Alert name:** `AuthLoginErrorRate` — login error rate > 5% over 5 minutes

## Symptoms

- Spike in failed logins or OAuth/OIDC rejections after a deployment.
- `auth-api` pods CrashLooping or returning 500s on `/token`.
- Session cookies not being set, or tokens marked invalid.

## Detection checks

1. Correlate with the latest `auth-api` deploy via `correlate_deployments`.
2. Check OIDC discovery endpoint and signing-key (JWKS) freshness.
3. Verify `redis-cache` (token store) health — `auth-api` depends on it.
4. Confirm clock skew is within tolerance (token `iat`/`exp` validation).
5. Inspect pod restarts and OOM kills.

## Detection / detection checks SQL

```sql
-- Recent failed login events from the audit store
SELECT reason, count(*) FROM auth_events
WHERE event = 'login_failed' AND ts > now() - interval '15 minutes'
GROUP BY reason ORDER BY 2 DESC;
```

## Recommended steps

1. If a config/deploy disabled the session cookie or rotated keys, roll back (RB-010).
2. If JWKS is stale/cached, force a key refresh and clear the discovery cache.
3. If `redis-cache` is degraded, follow RB-008 before retrying logins.
4. Re-issue signing keys only with identity team approval.

## Dangerous actions warning

- Do NOT delete or rotate signing keys without identity team approval — this
  invalidates all active sessions.
- Do NOT bypass MFA to "unblock" logins.

## Escalation path

- **Tier-1:** Steps 1–3 when a runbook clearly applies and no key rotation needed.
- **identity-oncall:** Error rate > 5% for 10 minutes or key rotation required.
- **P1:** 100% of users cannot log in → page `identity-l2 -> identity-oncall`.

## Business / regulatory impact

Login outage blocks all authenticated play and deposits. In regulated markets
this is a reportable availability incident.

## Tags / services

`auth-api`, `identity`, `oidc`, `jwks`, `mfa`, `redis-cache`, `login`
