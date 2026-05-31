# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-05-31 19:14:29 UTC
- **Corpus:** s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/
- **Cases:** 4 grounded runbook answers + 1 off-topic refusal

## 1. How do I triage an authentication service incident?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `auth_service_runbook.md`

**Answer:**

To triage an authentication service incident, follow these steps:

1. **Confirm the scope of the incident.** Check the auth service dashboard for the global error rate. If `auth_login_errors_total` is above 5% over the last 5 minutes, declare a P2 immediately. Above 25% → P1. 2. **Check recent deployments.** Use the command `kubectl -n auth get deploy -o wide`. If the latest rollout is less than 30 minutes old, treat the deployment as the likely cause and prepare a rollback. 3. **Check upstream dependencies.** Confirm that Redis (session store) and Postgres (user table) are healthy in the Service Map view before suspecting the auth service itself. 4. **Validate the OIDC discovery document.** Use the command `cu…

---

## 2. Which runbook should I follow for database connectivity issues?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `database_connectivity_runbook.md`

**Answer:**

For database connectivity issues, you should follow the "Database Connectivity Runbook". This runbook is specifically designed to address problems related to database connectivity, such as applications logging "connection refused", "too many connections", or "SSL handshake failed", and other symptoms like high p95 query latency or replication lag.

---

## 3. What are the escalation steps for a P1 production outage?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `escalation_policy.pdf`

**Answer:**

For a P1 production outage, the escalation steps are as follows:

1. The primary on-call engineer is paged immediately.

2. If the primary on-call engineer does not acknowledge the page within 8 minutes, the secondary on-call engineer is paged automatically.

3. If the secondary on-call engineer does not acknowledge the page within an additional 8 minutes, the engineering manager on call is paged.

4. The engineering manager on call should be woken for any P1 incident that lasts more than 30 minutes, any incident where customer data confidentiality, integrity, or availability is at risk, or any incident involving payment processing.

5. All P1/P2 incidents require updates in the #incident channel every 15 minutes,…

---

## 4. What should I check first when users cannot log in after a deployment?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `auth_service_runbook.md`

**Answer:**

When users cannot log in after a deployment, the first thing to check is recent deployments. If the latest rollout of the `auth-api` is less than 30 minutes old, treat the deployment as the likely cause and prepare a rollback.

---

## 5. What is the best restaurant in Tokyo?

- **Grounded:** `False` · **Citations:** 0

**Answer:**

The model cannot find sufficient information to answer the question about the best restaurant in Tokyo. The provided search results do not contain any information related to restaurants in Tokyo.

---
