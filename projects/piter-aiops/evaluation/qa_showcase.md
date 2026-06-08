# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-06-08 09:32:20 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Corpus:** s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/
- **Cases:** 4 grounded runbook answers + 1 off-topic refusal

## 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `runbook_db_cpu.md`, `runbook_db_cpu.md`

**Answer:**

Priority:

P2 (P1 if checkout/auth is blocked). A 95% CPU on the production primary database is a high-severity incident with immediate SLA and settlement processing risk. Investigation findings:

The applicable runbook is RB-007: Postgres CPU above 90% on prod-db-* hosts. The 95% CPU on prod-db-1 is typically driven by long-running analytics queries or missing indexes introduced in a recent deploy. Query latency will rise across dependent services (settlement, checkout, auth). The alert triggers when CPU exceeds 90% sustained for 5 minutes. Triage plan:

1. Confirm the alert and connect to prod-db-1 through the bastion host.

2. Run the detection SQL to identify active long-running queries and their duration.

3. C…

---

## 2. API 5xx rate is above 2% on checkout — what should I check?

- **Grounded:** `True` · **Citations:** 4
- **Sources:** `postmortem_2024_07.md`, `runbook_checkout_5xx.md`, `api_gateway_5xx_runbook.txt`, `api_gateway_5xx_runbook.txt`

**Answer:**

Priority:

P1. Checkout is revenue-critical and customer-facing. A 5xx rate above 2% for 4+ minutes triggers escalation. Historical precedent shows a similar incident in July 2024 peaked at 12% and caused measurable revenue impact within 47 minutes. Investigation findings:

A prior checkout outage was caused by an N+1 database query that saturated Postgres CPU. The alert fired 5 minutes after a bad deploy shipped. The error rate climbed to 12% before rollback restored service. This suggests deployment correlation and database load are the most likely culprits in checkout 5xx incidents. Triage plan:

1. Check recent deployments — correlate the 5xx spike timestamp with the last checkout-api release.

2. Tail checkout…

---

## 3. Queue lag is above 30 seconds — what should I do?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `runbook_queue_lag.md`, `runbook_kafka_consumer_lag.md`

**Answer:**

Priority:

P3 (P2 if lag exceeds 2 minutes or dead-letter queue is growing). The classification depends on which queue system you are running and whether customer-facing services are affected. Investigation findings:

First, identify which queue system is lagging. If this is an email-worker or generic message queue (not Kafka settlement), the alert threshold is 30 seconds sustained over 5 minutes. If this is a Kafka consumer group feeding settlement or analytics, different thresholds apply (100k messages or rising trend). Check worker pod health for restarts or out-of-memory kills, compare current queue depth to baseline for the time of day, and review recent deployments that may have introduced slower handlers o…

---

## 4. Users cannot log in after deployment — what should I check?

- **Grounded:** `True` · **Citations:** 4
- **Sources:** `runbook_auth_login.md`, `runbook_auth_login.md`, `auth_service_runbook.md`, `auth_service_runbook.md`

**Answer:**

Priority:

P2 if error rate is 5–25%; P1 if above 25% or all users affected. Login outages block all authenticated access and are reportable in regulated markets. Investigation findings:

When login breaks immediately after deployment, the deployment itself is the likely cause. Check whether the latest auth-api rollout occurred within the last 30 minutes. Verify that the error spike in auth_login_errors_total correlates with the deploy timestamp. The runbooks identify three common failure modes: pod crashes or 502/504 responses (ingress or readiness issue), 401 errors for valid credentials (session store degradation), and MFA challenges not arriving (provider issue). Triage plan:

1. Confirm scope: check the auth…

---

## 5. How do I decide if an alert should be resolved at Tier 1 or escalated?

- **Grounded:** `True` · **Citations:** 3
- **Sources:** `tier1_escalation_guide.md`, `monitoring_alerts_reference.md`, `escalation_policy.pdf`

**Answer:**

**Resolve at Tier 1 when:**

1. The runbook contains deterministic, safe actions you can execute (health checks, log inspection, worker scaling, approved database queries).

2. Customer impact is low or isolated—affecting a single pod, non-production environment, or rated P3.

3. A recent deployment clearly caused the issue and rollback procedures allow immediate safe rollback.

4. The alert matches a known pattern from your incident history with documented resolution steps.

**Escalate when:**

1. Customer impact is high—authentication, checkout, or payment flows are degraded (P1/P2 severity).

2. Data loss, security breach, payment processing failure, or production-wide outage is possible.

3. The runbook explicit…

---
