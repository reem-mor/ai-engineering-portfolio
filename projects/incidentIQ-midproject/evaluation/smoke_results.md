# Bedrock KB Smoke Test Results

- **Run at:** 2026-06-03 07:15:55 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.amazon.nova-lite-v1:0`
- **Score:** 7/7 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | Postgres CPU is 95% on prod-db-1 — what is the runbook? | True | 1 | **PASS** |
| 2 | API 5xx rate is above 2% on checkout — what should I check? | True | 1 | **PASS** |
| 3 | Queue lag is above 30 seconds — what should I do? | True | 1 | **PASS** |
| 4 | Users cannot log in after deployment — what should I check? | True | 1 | **PASS** |
| 5 | How do I decide if an alert should be resolved at Tier 1 or escalated? | True | 1 | **PASS** |
| 6 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |
| 7 | what is the | None | 0 | **PASS** |

## Details

### 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: The runbook for Postgres CPU above 90% on prod-db-1 is `runbook_db_cpu.md`.  Recommended steps: 1. Confirm the alert and identify long-running queries. 2. Connect through the bastion host to the affected primary. 3. Run the followi

### 2. API 5xx rate is above 2% on checkout — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Check recent deployments, service logs, database CPU, and dependency errors.  Recommended steps: 1. Check recent deployments — correlate 5xx spike with the last release timestamp. 2. Check service logs — tail checkout-api and gatew

### 3. Queue lag is above 30 seconds — what should I do?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Check worker health, queue depth, recent deploys, scale workers if allowed, inspect dead-letter queue, and escalate if necessary.  Recommended steps: 1. Check worker health — pod status, restarts, OOM kills in the worker namespace.

### 4. Users cannot log in after deployment — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Check recent deployments, auth-service health, logs, environment variables, and database connectivity.  Recommended steps: 1. Check recent deployments using `kubectl -n auth get deploy -o wide`. 2. Check auth-service health endpoin

### 5. How do I decide if an alert should be resolved at Tier 1 or escalated?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Use the Tier-1 vs Escalation Decision Guide to determine if an alert should be resolved at Tier 1 or escalated.  Recommended steps: 1. Check if the runbook has deterministic, safe actions and if the customer impact is low or isolat

### 6. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: The model cannot find sufficient information to answer the question.

### 7. what is the
- Status: **PASS**
- Grounded: `None` · Citations: `0`
- Answer preview: 
