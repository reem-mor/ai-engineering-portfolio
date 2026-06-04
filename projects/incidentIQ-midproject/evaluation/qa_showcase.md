# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-06-04 07:55:10 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Corpus:** s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/
- **Cases:** 4 grounded runbook answers + 1 off-topic refusal

## 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `monitoring_alerts_reference.md`, `runbook_db_cpu.md`

**Answer:**

Summary:

The runbook for Postgres CPU above 90% on prod-db-1 is `runbook_db_cpu.md`.

Recommended steps:

1. Confirm the alert and connect to the affected primary through the bastion host

2. Query `pg_stat_activity` to identify long-running queries and their duration

3. Cancel queries running longer than 5 minutes using `pg_cancel_backend(pid)`

4. Terminate backends only if cancel fails

5. Check for missing indexes by reviewing `seq_scan` vs `idx_scan` ratios in `pg_stat_user_tables`

6. If load persists, fail over to the replica using Patroni (`patronictl failover`)

Escalation:

- Escalate to DBA on-call if CPU remains above 90% for 15 minutes, if failover is required, or if cancel/terminate commands are ineffec…

---

## 2. API 5xx rate is above 2% on checkout — what should I check?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `runbook_checkout_5xx.md`, `postmortem_2024_07.md`

**Answer:**

Summary:

Check recent deployments, service logs, database CPU, and dependencies in that order to identify why checkout API is returning errors above the 2% threshold. Recommended steps:

1. Check recent deployments — correlate the 5xx spike with the last release timestamp

2. Check service logs — tail checkout-api and gateway logs for ERROR messages and stack traces

3. Check database CPU and slow queries — run the database CPU runbook if Postgres is under load

4. Check dependency errors — verify payment service, inventory, and auth token validation are healthy

5. Roll back the recent deployment if the issue clearly correlates with it

6. If error rate persists above 2% for 10 minutes, page the checkout service own…

---

## 3. Queue lag is above 30 seconds — what should I do?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `runbook_queue_lag.md`

**Answer:**

Summary:

Check worker health and queue depth, then scale workers if needed; escalate if lag continues to grow or the dead-letter queue shows abnormal activity. Recommended steps:

1. Check worker pod status for restarts or out-of-memory kills in the worker namespace

2. Compare current queue depth to your baseline for this time of day

3. Review recent worker deployments for slower handlers or configuration changes

4. Scale up worker replicas within your autoscaling limits

5. Inspect the dead-letter queue for failed or poison-pill messages that may be blocking progress

6. Escalate if lag continues increasing after scaling or if DLQ activity is abnormal Escalation:

- Tier-1 can handle scaling and DLQ replay when st…

---

## 4. Users cannot log in after deployment — what should I check?

- **Grounded:** `True` · **Citations:** 4
- **Sources:** `auth_service_runbook.md`, `runbook_auth_login.md`, `monitoring_alerts_reference.md`, `alerts_last_3mo.json`

**Answer:**

Summary:

Check if the recent deployment caused the login failure, then verify auth service health and upstream dependencies (Redis and Postgres). Recommended steps:

1. Confirm the scope by checking the auth service dashboard for global error rate — if above 5% over 5 minutes, it's P2; above 25% is P1.

2. Check recent deployments with `kubectl -n auth get deploy -o wide` — if the latest rollout is less than 30 minutes old, treat it as the likely cause.

3. Verify auth-service health endpoints return 200 by hitting `/health` and `/ready`.

4. Check auth-service logs for OIDC, token, and database connection errors.

5. Validate critical environment variables: `JWT_SECRET`, `AUTH_DB_URL`, and `TOKEN_ISSUER`.

6. Confir…

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
