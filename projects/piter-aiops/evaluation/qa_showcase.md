# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-06-06 07:58:18 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Corpus:** s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/
- **Cases:** 4 grounded runbook answers + 1 off-topic refusal

## 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_db_cpu.md`

**Answer:**

Summary:

Follow RB-007 (Postgres CPU above 90% on prod-db-* hosts) to diagnose and resolve the high CPU on prod-db-1.

Recommended steps:

1. Confirm the alert and connect to prod-db-1 through the bastion host.

2. Identify long-running queries using `pg_stat_activity` and find active queries ordered by duration.

3. Cancel queries running longer than 5 minutes using `pg_cancel_backend()`.

4. Terminate the backend only if cancel fails, using `pg_terminate_backend()`.

5. Check for missing indexes using `pg_stat_user_tables`.

6. If load persists, fail over to the replica using Patroni (`patronictl failover`).

7. Escalate to DBA on-call if CPU remains above 90% for 15 minutes.

Escalation:

- When to escalate: CPU > 9…

---

## 2. API 5xx rate is above 2% on checkout — what should I check?

- **Grounded:** `True` · **Citations:** 3
- **Sources:** `runbook_checkout_5xx.md`, `postmortem_2024_07.md`, `api_gateway_5xx_runbook.txt`

**Answer:**

Summary:

Check recent deployments, service logs, database CPU, and dependencies in that order, then roll back if a bad deploy is found. Recommended steps:

1. Check recent deployments — correlate the 5xx spike with the last release timestamp

2. Check service logs — tail checkout-api and gateway logs for ERROR messages and stack traces

3. Check database CPU and slow queries — run the database CPU runbook if Postgres is hot (a prior checkout outage was caused by an N+1 query saturating database CPU)

4. Check dependency errors — verify payment service, inventory, and auth token validation are healthy

5. Roll back the deployment if the issue matches a recent bad release Escalation:

- When to escalate: If error rate…

---

## 3. Queue lag is above 30 seconds — what should I do?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_queue_lag.md`

**Answer:**

Summary:

Check worker health and queue depth, then scale workers if needed to reduce lag below 30 seconds. Recommended steps:

1. Check worker health — verify pod status, restarts, and out-of-memory kills in the worker namespace

2. Check queue depth — compare current depth to baseline for this time of day

3. Check recent deploys — a new worker version may have slower handlers or bad configuration

4. Scale workers if allowed — increase replica count within autoscaling limits

5. Inspect dead-letter queue — failed messages may block progress or indicate poison pills

6. Escalate if lag keeps increasing after scale-up or dead-letter queue rate is abnormal Escalation:

- When to escalate: If lag continues to increase a…

---

## 4. Users cannot log in after deployment — what should I check?

- **Grounded:** `True` · **Citations:** 4
- **Sources:** `auth_service_runbook.md`, `runbook_auth_login.md`, `auth_service_runbook.md`, `runbook_auth_login.md`

**Answer:**

Summary:

Check if the latest deployment to auth-api occurred within the last 30 minutes, as post-deployment login failures are usually caused by the recent rollout.

Recommended steps:

1. Confirm the scope by checking the auth service dashboard for error rate — if login errors exceed 5% over 5 minutes, declare P2; above 25% declare P1.

2. Check recent deployments using `kubectl -n auth get deploy -o wide` — if the latest rollout is less than 30 minutes old, treat it as the likely cause.

3. Check upstream dependencies (Redis session store and Postgres user table) are healthy via the Service Map view.

4. Validate the OIDC discovery document with `curl -sS https://auth.example.com/.well-known/openid-configuration…

---

## 5. How do I decide if an alert should be resolved at Tier 1 or escalated?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `tier1_escalation_guide.md`, `escalation_policy.pdf`

**Answer:**

Summary:

Resolve at Tier 1 if the runbook has safe, deterministic actions and customer impact is low; escalate if customer impact is high, data loss or security is at risk, the runbook requires a specialist, or Tier 1 actions don't improve the alert within 15 minutes. Recommended steps:

1. Check the alert severity (P1/P2 = escalate; P3/P4 = likely Tier 1)

2. Review the runbook for the alert to see if it lists deterministic, safe actions you can perform

3. Assess customer impact — if checkout, auth, or payment flows are degraded, escalate immediately

4. Look up the alert in recent history to see if it matches a known, documented resolution pattern

5. If the runbook explicitly requires a DBA, DevOps, backend owne…

---
