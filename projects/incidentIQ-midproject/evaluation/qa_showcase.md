# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-06-03 07:15:55 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.amazon.nova-lite-v1:0`
- **Corpus:** s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/
- **Cases:** 4 grounded runbook answers + 1 off-topic refusal

## 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_db_cpu.md`

**Answer:**

Summary:

The runbook for Postgres CPU above 90% on prod-db-1 is `runbook_db_cpu.md`.

Recommended steps:

1. Confirm the alert and identify long-running queries.

2. Connect through the bastion host to the affected primary.

3. Run the following against `pg_stat_activity`:

```sql

SELECT pid, usename, state, now() - query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duration DESC;

```

4. Cancel queries running longer than 5 minutes:

```sql

SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '5 minutes';

```

5. Terminate the backend only if cancel fails:

```sql

SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid…

---

## 2. API 5xx rate is above 2% on checkout — what should I check?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_checkout_5xx.md`

**Answer:**

Summary:

Check recent deployments, service logs, database CPU, and dependency errors.

Recommended steps:

1. Check recent deployments — correlate 5xx spike with the last release timestamp.

2. Check service logs — tail checkout-api and gateway logs for ERROR and stack traces.

3. Check database CPU and slow queries — run `runbook_db_cpu.md` if Postgres is hot.

4. Check dependency errors — payment service, inventory, auth token validation.

5. Roll back if the issue matches a recent bad deployment (see `deployment_rollback_sop.docx`).

6. Escalate according to severity — page checkout service owner if error rate stays above 2% for 10 minutes.

Escalation:

- When to escalate: If the error rate stays above 2% for 10 m…

---

## 3. Queue lag is above 30 seconds — what should I do?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_queue_lag.md`

**Answer:**

Summary:

Check worker health, queue depth, recent deploys, scale workers if allowed, inspect dead-letter queue, and escalate if necessary.

Recommended steps:

1. Check worker health — pod status, restarts, OOM kills in the worker namespace.

2. Check queue depth — compare current depth to baseline for this time of day.

3. Check recent deploys — new worker version may have slower handlers or bad config.

4. Scale workers if allowed — increase replica count within autoscaling limits.

5. Inspect dead-letter queue — failed messages may block progress or indicate poison pills.

6. Escalate if lag keeps increasing after scale-up or DLQ rate is abnormal.

Escalation:

- When to escalate: If lag keeps increasing after scal…

---

## 4. Users cannot log in after deployment — what should I check?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_auth_login.md`

**Answer:**

Summary:

Check recent deployments, auth-service health, logs, environment variables, and database connectivity.

Recommended steps:

1. Check recent deployments using `kubectl -n auth get deploy -o wide`.

2. Check auth-service health endpoint — `/health` and `/ready` must return 200.

3. Check auth-service logs for OIDC, token, and database connection errors.

4. Validate environment variables: `JWT_SECRET`, `AUTH_DB_URL`, `TOKEN_ISSUER`.

5. Check database connectivity — Postgres and Redis session store must be healthy.

Escalation:

- When to escalate: If login failure rate is above 25% or complete auth outage.

- Who to escalate to: Auth team / security for suspected credential leak, OIDC provider outage, or JWT m…

---

## 5. How do I decide if an alert should be resolved at Tier 1 or escalated?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `tier1_escalation_guide.md`

**Answer:**

Summary:

Use the Tier-1 vs Escalation Decision Guide to determine if an alert should be resolved at Tier 1 or escalated.

Recommended steps:

1. Check if the runbook has deterministic, safe actions and if the customer impact is low or isolated.

2. Determine if a recent deploy caused the issue and if a rollback is possible.

3. Verify if the alert matches a known pattern with documented resolution.

4. Assess if the customer impact is high, if data loss or security breach is possible, or if the runbook requires specialized teams.

5. Evaluate if Tier-1 actions did not improve the signal within the runbook time box.

6. If unsure, escalate early with prepared notes.

Escalation:

- When to escalate: If the customer imp…

---
