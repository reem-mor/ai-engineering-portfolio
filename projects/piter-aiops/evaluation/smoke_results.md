# Bedrock KB Smoke Test Results

- **Run at:** 2026-06-08 09:32:20 UTC
- **Model:** `arn:aws:bedrock:us-east-1:329597159579:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0`
- **Score:** 7/7 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | Postgres CPU is 95% on prod-db-1 — what is the runbook? | True | 2 | **PASS** |
| 2 | API 5xx rate is above 2% on checkout — what should I check? | True | 4 | **PASS** |
| 3 | Queue lag is above 30 seconds — what should I do? | True | 2 | **PASS** |
| 4 | Users cannot log in after deployment — what should I check? | True | 4 | **PASS** |
| 5 | How do I decide if an alert should be resolved at Tier 1 or escalated? | True | 3 | **PASS** |
| 6 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |
| 7 | what is the | None | 0 | **PASS** |

## Details

### 1. Postgres CPU is 95% on prod-db-1 — what is the runbook?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Priority: P2 (P1 if checkout/auth is blocked). A 95% CPU on the production primary database is a high-severity incident with immediate SLA and settlement processing risk. Investigation findings: The applicable runbook is RB-007: Postgres CP

### 2. API 5xx rate is above 2% on checkout — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `4`
- Answer preview: Priority: P1. Checkout is revenue-critical and customer-facing. A 5xx rate above 2% for 4+ minutes triggers escalation. Historical precedent shows a similar incident in July 2024 peaked at 12% and caused measurable revenue impact within 47 

### 3. Queue lag is above 30 seconds — what should I do?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Priority: P3 (P2 if lag exceeds 2 minutes or dead-letter queue is growing). The classification depends on which queue system you are running and whether customer-facing services are affected. Investigation findings: First, identify which qu

### 4. Users cannot log in after deployment — what should I check?
- Status: **PASS**
- Grounded: `True` · Citations: `4`
- Answer preview: Priority: P2 if error rate is 5–25%; P1 if above 25% or all users affected. Login outages block all authenticated access and are reportable in regulated markets. Investigation findings: When login breaks immediately after deployment, the de

### 5. How do I decide if an alert should be resolved at Tier 1 or escalated?
- Status: **PASS**
- Grounded: `True` · Citations: `3`
- Answer preview: **Resolve at Tier 1 when:**  1. The runbook contains deterministic, safe actions you can execute (health checks, log inspection, worker scaling, approved database queries). 2. Customer impact is low or isolated—affecting a single pod, non-p

### 6. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: I cannot answer this question. The search results provided contain only enterprise incident-response documentation, runbooks, and alert procedures for database and application infrastructure. They do not contain any information about restau

### 7. what is the
- Status: **PASS**
- Grounded: `None` · Citations: `0`
- Answer preview: 
