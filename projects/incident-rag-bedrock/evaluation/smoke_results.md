# Bedrock KB Smoke Test Results

- **Run at:** 2026-05-31 19:35:42 UTC
- **Score:** 6/6 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | How do I triage an authentication service incident? | True | 1 | **PASS** |
| 2 | Which runbook should I follow for database connectivity issues? | True | 1 | **PASS** |
| 3 | What are the escalation steps for a P1 production outage? | True | 1 | **PASS** |
| 4 | What should I check first when users cannot log in after a deployment? | True | 1 | **PASS** |
| 5 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |
| 6 | what is the | None | 0 | **PASS** |

## Details

### 1. How do I triage an authentication service incident?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: To triage an authentication service incident, follow these steps:  1. **Confirm the scope of the incident.** Check the authentication service dashboard for the global error rate. If `auth_login_errors_total` is above 5% over the last 5 minu

### 2. Which runbook should I follow for database connectivity issues?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: For database connectivity issues, you should follow the "Database Connectivity Runbook". This runbook is specifically designed to address issues related to database connectivity, such as applications logging "connection refused", "too many 

### 3. What are the escalation steps for a P1 production outage?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: For a P1 production outage, the escalation steps are as follows:  1. The primary on-call engineer is paged immediately. 2. If the primary on-call engineer does not acknowledge the page within 8 minutes, the secondary on-call engineer is pag

### 4. What should I check first when users cannot log in after a deployment?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: When users cannot log in after a deployment, the first thing to check is recent deployments. If the latest `auth-api` rollout is less than 30 minutes old, treat the deployment as the likely cause and prepare a rollback per the Standard reco

### 5. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: The model cannot find sufficient information to answer the question about the best restaurant in Tokyo. The provided search results do not contain any information related to restaurants in Tokyo.

### 6. what is the
- Status: **PASS**
- Grounded: `None` · Citations: `0`
- Answer preview: 
