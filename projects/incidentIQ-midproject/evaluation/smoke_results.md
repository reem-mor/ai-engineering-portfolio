# Bedrock KB Smoke Test Results

- **Run at:** 2026-06-04 07:55:10 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Score:** 7/7 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | Postgres CPU is 95% on prod-db-1 — what is the runbook? | True | 2 | **PASS** |
| 2 | API 5xx rate is above 2% on checkout — what should I check? | True | 2 | **PASS** |
| 3 | Queue lag is above 30 seconds — what should I do? | True | 1 | **PASS** |
| 4 | Users cannot log in after deployment — what should I check? | True | 4 | **PASS** |
| 5 | How do I decide if an alert should be resolved at Tier 1 or escalated? | True | 2 | **PASS** |
| 6 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |
| 7 | what is the | None | 0 | **PASS** |

## Details

### 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Summary: The runbook for Postgres CPU above 90% on prod-db-1 is `runbook_db_cpu.md`.  Recommended steps: 1. Confirm the alert and connect to the affected primary through the bastion host 2. Query `pg_stat_activity` to identify long-running 

### 2. API 5xx rate is above 2% on checkout — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Summary: Check recent deployments, service logs, database CPU, and dependencies in that order to identify why checkout API is returning errors above the 2% threshold. Recommended steps: 1. Check recent deployments — correlate the 5xx spike 

### 3. Queue lag is above 30 seconds — what should I do?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: Summary: Check worker health and queue depth, then scale workers if needed; escalate if lag continues to grow or the dead-letter queue shows abnormal activity. Recommended steps: 1. Check worker pod status for restarts or out-of-memory kill

### 4. Users cannot log in after deployment — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `4`
- Answer preview: Summary: Check if the recent deployment caused the login failure, then verify auth service health and upstream dependencies (Redis and Postgres). Recommended steps: 1. Confirm the scope by checking the auth service dashboard for global erro

### 5. How do I decide if an alert should be resolved at Tier 1 or escalated?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Summary: Resolve at Tier 1 if the runbook has safe, deterministic actions and customer impact is low; escalate if customer impact is high, data loss or security is at risk, the runbook requires a specialist, or Tier 1 actions don't improve 

### 6. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: I cannot answer this question. I am IncidentIQ, an NOC assistant designed to help with infrastructure incidents, alerts, and runbooks. The search results contain only incident management documentation, postmortems, and alert runbooks—nothin

### 7. what is the
- Status: **PASS**
- Grounded: `None` · Citations: `0`
- Answer preview: 
