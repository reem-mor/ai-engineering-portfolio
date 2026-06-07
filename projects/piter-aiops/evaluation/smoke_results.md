# Bedrock KB Smoke Test Results

- **Run at:** 2026-06-06 07:58:18 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Score:** 7/7 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | Postgres CPU is 95% on prod-db-1 — what is the runbook? | True | 1 | **PASS** |
| 2 | API 5xx rate is above 2% on checkout — what should I check? | True | 3 | **PASS** |
| 3 | Queue lag is above 30 seconds — what should I do? | True | 1 | **PASS** |
| 4 | Users cannot log in after deployment — what should I check? | True | 4 | **PASS** |
| 5 | How do I decide if an alert should be resolved at Tier 1 or escalated? | True | 2 | **PASS** |
| 6 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |
| 7 | what is the | None | 0 | **PASS** |

## Details

### 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Follow RB-007 (Postgres CPU above 90% on prod-db-* hosts) to diagnose and resolve the high CPU on prod-db-1.  Recommended steps: 1. Confirm the alert and connect to prod-db-1 through the bastion host. 2. Identify long-running queri

### 2. API 5xx rate is above 2% on checkout — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `3`
- Answer preview: Summary: Check recent deployments, service logs, database CPU, and dependencies in that order, then roll back if a bad deploy is found. Recommended steps: 1. Check recent deployments — correlate the 5xx spike with the last release timestamp

### 3. Queue lag is above 30 seconds — what should I do?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Check worker health and queue depth, then scale workers if needed to reduce lag below 30 seconds. Recommended steps: 1. Check worker health — verify pod status, restarts, and out-of-memory kills in the worker namespace 2. Check que

### 4. Users cannot log in after deployment — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `4`
- Answer preview: Summary: Check if the latest deployment to auth-api occurred within the last 30 minutes, as post-deployment login failures are usually caused by the recent rollout.  Recommended steps: 1. Confirm the scope by checking the auth service dashb

### 5. How do I decide if an alert should be resolved at Tier 1 or escalated?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Summary: Resolve at Tier 1 if the runbook has safe, deterministic actions and customer impact is low; escalate if customer impact is high, data loss or security is at risk, the runbook requires a specialist, or Tier 1 actions don't improve 

### 6. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: I cannot answer this question. The search results contain only internal NOC runbooks and alert documentation for infrastructure and database issues. They do not contain any information about restaurants in Tokyo or anywhere else.  To get re

### 7. what is the
- Status: **PASS**
- Grounded: `None` · Citations: `0`
- Answer preview: 
