# Sample Questions and Answers — Live Bedrock KB

- **Run at:** 2026-05-31 11:27:27 UTC
- **Corpus:** s3://reem-amdocs-ai-artifacts-3331/projects/incident-rag-bedrock/data/sample_documents/
- **Cases:** 3 grounded runbook answers + 1 off-topic refusal

## 1. How do I triage an authentication service incident?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `auth_service_runbook.md`

**Answer:**

To triage an authentication service incident, follow these steps:

1. **Confirm the scope:** Check the auth service dashboard for the global error rate. If `auth_login_errors_total` is above 5% over the last 5 minutes, declare a P2 immediately. Above 25% → P1.

2. **Check recent deployments:** If the latest rollout is < 30 minutes old, treat it as the likely cause.

3. **Check upstream dependencies:** Confirm that Redis (session store) and Postgres (user table) are healthy in the Service Map view before suspecting auth itself.

4. **Validate the OIDC discovery document:** If the public ingress is broken, escalate to the platform team.

5. **Triage decision tree:** Based on the symptoms, follow the appropriate steps…

---

## 2. Which runbook should I follow for database connectivity issues?

- **Grounded:** `True` · **Citations:** 2
- **Sources:** `monitoring_alerts_reference.md`, `database_connectivity_runbook.md`

**Answer:**

Based on the search results, you should follow the `database_connectivity_runbook.md` for database connectivity issues. This runbook is specifically designed to address issues related to database connectivity, such as applications logging "connection refused," "too many connections," or "SSL handshake failed," and sustained p95 query latency above 1 second for 5 minutes. It provides detailed steps and checks for both PostgreSQL and Redis databases to help diagnose and resolve connectivity issues.

---

## 3. What are the escalation steps for a P1 production outage?

- **Grounded:** `True` · **Citations:** 1
- **Sources:** `escalation_policy.pdf`

**Answer:**

The escalation steps for a P1 production outage are as follows:

1. The primary on-call engineer is paged immediately.

2. If the primary on-call engineer does not acknowledge the incident within 8 minutes, the secondary on-call engineer is paged automatically.

3. If the secondary on-call engineer does not acknowledge the incident within an additional 8 minutes, the engineering manager on call is paged.

4. The engineering manager on call should be woken for any P1 incident lasting more than 30 minutes, any incident where customer data confidentiality, integrity, or availability is at risk, or any incident involving payment processing.

Additionally, all P1/P2 incidents require updates in the #incident channel ev…

---

## 5. What is the best restaurant in Tokyo?

- **Grounded:** `False` · **Citations:** 0

**Answer:**

The model cannot find sufficient information to answer the question about the best restaurant in Tokyo. The search results provided do not contain any information related to restaurants in Tokyo.

---
