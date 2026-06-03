# Runbook: Users cannot log in after deployment

**Severity:** P2 when login failure rate > 5%; P1 when > 25%  
**Service:** auth-service  
**Alert:** `AuthLoginFailureRate` — login failures > 5% for 5m

## Recommended steps

1. Check auth-service health endpoint — `/health` and `/ready` must return 200.
2. Check auth-service logs — search for OIDC, token, and database connection errors.
3. Review recent release notes — confirm config or secret changes in the last deploy.
4. Validate environment variables: `JWT_SECRET`, `AUTH_DB_URL`, `TOKEN_ISSUER`.
5. Check database connectivity — Postgres and Redis session store must be healthy.
6. Review token expiration settings — clock skew or shortened TTL can mass-fail logins.
7. Roll back the deployment if many users are affected and rollback SOP allows it.

## Escalation

- **Tier-1:** Rollback when deploy correlation is clear within 30 minutes of release.
- **Auth team / security:** Suspected credential leak, OIDC provider outage, or JWT misconfiguration.
- **P1:** Login failure rate above 25% or complete auth outage.

## Related documents

- `auth_service_runbook.md` — extended auth triage
- `deployment_rollback_sop.docx` — rollback procedure
- `escalation_policy.pdf` — P1/P2 paging rules
