# RB-002: Runbook — Users cannot log in after deployment

**Runbook ID:** RB-002  
**Severity:** P1 (all users) / P2 (subset)  
**Service:** auth-service / `auth-api` in `NJ-DGE`, `GIB`, `MGM`  
**Alert:** `AuthLoginFailureRate` — login failures > 5% for 5m

## Symptoms

- Spike in failed logins or OAuth/OIDC rejections after a deployment.
- `auth-api` pods CrashLooping or returning 500s on `/token`.
- Session cookies not being set, or tokens marked invalid.

## Detection checks

1. Check auth-service health endpoint — `/health` and `/ready` must return 200.
2. Correlate with the latest `auth-api` deploy via `correlate_deployments`.
3. Check OIDC discovery endpoint and signing-key (JWKS) freshness.
4. Verify `redis-cache` (token store) health — follow `runbook_redis_token_store.md`.
5. Confirm clock skew is within tolerance (token `iat`/`exp` validation).
6. Inspect pod restarts and OOM kills.

## Detection SQL

```sql
-- Recent failed login events from the audit store
SELECT reason, count(*) FROM auth_events
WHERE event = 'login_failed' AND ts > now() - interval '15 minutes'
GROUP BY reason ORDER BY 2 DESC;
```

## Recommended steps

1. Check auth-service logs — search for OIDC, token, and database connection errors.
2. Review recent release notes — confirm config or secret changes in the last deploy.
3. Validate environment variables: `JWT_SECRET`, `AUTH_DB_URL`, `TOKEN_ISSUER`.
4. If a config/deploy disabled the session cookie or rotated keys, roll back (`runbook_deployment_rollback.md`).
5. If JWKS is stale/cached, force a key refresh and clear the discovery cache.
6. If `redis-cache` is degraded, follow `runbook_redis_token_store.md` before retrying logins.
7. Roll back the deployment if many users are affected and rollback SOP allows it.

## Dangerous actions warning

- Do NOT delete or rotate signing keys without identity team approval — this
  invalidates all active sessions.
- Do NOT bypass MFA to "unblock" logins.

## Escalation

- **Tier-1:** Steps 1–4 when a runbook clearly applies and no key rotation needed.
- **Auth team / identity on-call:** Error rate > 5% for 10 minutes or key rotation required.
- **P1:** Login failure rate above 25%, 100% of users cannot log in, or complete auth outage.

## Business / regulatory impact

Login outage blocks all authenticated play and deposits. In regulated markets
this is a reportable availability incident.

## Related documents

- `auth_service_runbook.md` — extended auth triage
- `runbook_deployment_rollback.md` — rollback procedure
- `runbook_redis_token_store.md` — token store degradation (RB-008)
- `escalation_policy.pdf` — P1/P2 paging rules
