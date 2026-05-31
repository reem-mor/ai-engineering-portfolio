# Bedrock KB Smoke Test Results

- **Run at:** 2026-05-31 10:18:51 UTC
- **Score:** 5/5 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | How do I triage an authentication service incident? | True | 9 | **PASS** |
| 2 | Which runbook should I follow for database connectivity issues? | True | 3 | **PASS** |
| 3 | What are the escalation steps for a P1 production outage? | True | 5 | **PASS** |
| 4 | What should I check first when users cannot log in after a deployment? | True | 7 | **PASS** |
| 5 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |

## Details

### 1. How do I triage an authentication service incident?
- Status: **PASS**
- Grounded: `True` · Citations: `9`
- Answer preview: To triage an authentication service incident, follow these steps:  1. Confirm the scope of the incident by checking the auth service dashboard for the global error rate. If `auth_login_errors_total` is above 5% over the last 5 minutes, decl

### 2. Which runbook should I follow for database connectivity issues?
- Status: **PASS**
- Grounded: `True` · Citations: `3`
- Answer preview: Based on the search results, you should follow the "Database Connectivity Runbook" for database connectivity issues. This runbook applies to PostgreSQL primary + replicas, Redis session/cache layer, and covers symptoms such as applications 

### 3. What are the escalation steps for a P1 production outage?
- Status: **PASS**
- Grounded: `True` · Citations: `5`
- Answer preview: Answer: The escalation steps for a P1 production outage are as follows:  1. The primary on-call engineer is paged immediately. 2. If the primary on-call engineer does not acknowledge the incident within 8 minutes, the secondary on-call engi

### 4. What should I check first when users cannot log in after a deployment?
- Status: **PASS**
- Grounded: `True` · Citations: `7`
- Answer preview: Plan  1. Read and understand the user's question. 2. Identify relevant information from the search results. 3. Summarize the answer based on the relevant information.  Answer  When users cannot log in after a deployment, the first checks yo

### 5. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: The model cannot find sufficient information to answer the question about the best restaurant in Tokyo. The search results provided do not contain any information related to restaurants in Tokyo.
