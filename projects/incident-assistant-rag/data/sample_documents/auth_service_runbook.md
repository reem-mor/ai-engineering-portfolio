# Auth Service Runbook

## Overview

The auth-service handles user login, password authentication, JWT token validation, refresh tokens, and user session creation. Production login failures are high priority because users may be blocked from the product.

## Common Symptoms

- Users cannot log in.
- Login API returns HTTP 401, 403, or 500.
- JWT token validation fails.
- Users report being logged out repeatedly.
- Login failures started after a recent deployment.
- Auth-service health check is failing or unstable.

## First Checks

1. Check the auth-service health endpoint.
2. Check auth-service logs for authentication errors.
3. Check recent deployments and release notes.
4. Verify environment variables related to JWT_SECRET, AUTH_DB_URL, and TOKEN_ISSUER.
5. Check database connectivity from auth-service.
6. Confirm that token expiration settings were not changed.

## Useful Log Patterns

- `invalid jwt signature`
- `token issuer mismatch`
- `database connection refused`
- `password verification failed`
- `auth provider timeout`

## Safe Actions

- Do not rotate JWT secrets during an active incident without backend approval.
- Do not restart all auth pods at once if traffic is high.
- Check one pod first, then compare logs across pods.
- If a recent deployment caused the issue, prepare rollback after confirming user impact.

## Escalation

If many users cannot log in in production, classify the incident as High severity and escalate to the backend team. If all users are affected, escalate immediately to the incident commander and service owner.
