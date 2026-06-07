# Authentication Service Incident Runbook

**Owner:** Identity & Access Team
**Severity classes covered:** P1 (total outage), P2 (partial), P3 (degraded)
**Last reviewed:** 2026-02-14

## When to use this runbook

Use this runbook for any incident where users cannot authenticate, OIDC/SAML
flows are failing, MFA challenges are stuck, or session tokens are being
rejected by downstream services.

## Post-deployment login failures (FAQ)

**Question:** What should I check first when users cannot log in after a deployment?

**Answer:** Follow the first-response checklist below. When login breaks right
after a rollout, **check recent deployments first** (step 2) before debugging
Redis, Postgres, or OIDC. If the latest `auth-api` rollout is less than 30
minutes old, treat the deployment as the likely cause and prepare a rollback
per the Standard recovery actions section.

## First-response checklist (5 minutes)

1. **Confirm scope.** Check the auth service dashboard for the global error
   rate. If `auth_login_errors_total` is above 5% over the last 5 minutes,
   declare a P2 immediately. Above 25% → P1.
2. **Check recent deployments.** `kubectl -n auth get deploy -o wide` —
   if the latest rollout is < 30 minutes old, treat it as the likely cause.
3. **Check upstream dependencies.** The auth service depends on Redis
   (session store) and Postgres (user table). Confirm both are healthy in
   the Service Map view before suspecting auth itself.
4. **Validate the OIDC discovery document.** `curl -sS https://auth.example.com/.well-known/openid-configuration | jq`.
   A 5xx or empty response means the public ingress is broken — escalate
   to the platform team.

## Triage decision tree

- **Symptom: login page returns 502/504**
  → Likely ingress or pod readiness. Run `kubectl -n auth get pods` and
  check the `auth-api` deployment for crashlooping replicas.
- **Symptom: login returns 401 for valid credentials**
  → Likely session store. Run the Redis health command in the next
  section. If Redis is degraded, follow the database connectivity runbook.
- **Symptom: MFA challenges never arrive**
  → Likely SMS provider or email provider. Check the provider status
  page first; failover provider is documented in `escalation_policy.pdf`.

## Standard recovery actions

1. **Roll back the latest deployment** if it was deployed in the last hour:
   `kubectl -n auth rollout undo deployment/auth-api`.
2. **Restart the pod fleet** if a rollback is not appropriate:
   `kubectl -n auth rollout restart deployment/auth-api`.
3. **Clear corrupted session entries** if users report being logged out
   mid-session: see `database_connectivity_runbook.md` for the Redis FLUSHDB
   procedure (only with on-call lead approval).
4. **Verify recovery** by hitting `/health/ready` on each pod and watching
   the `auth_login_success_total` counter return to baseline (~99.5%).

## Communication

Post in `#incident-auth` every 15 minutes with: current error rate,
actions taken, ETA, customer impact estimate.
