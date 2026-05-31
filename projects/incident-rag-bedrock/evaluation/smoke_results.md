# Bedrock KB Smoke Test Results

- **Run at:** 2026-05-31 11:27:27 UTC
- **Score:** 5/6 PASS

| # | Question | Grounded | Citations | Status |
|---|----------|----------|-----------|--------|
| 1 | How do I triage an authentication service incident? | True | 1 | **PASS** |
| 2 | Which runbook should I follow for database connectivity issues? | True | 2 | **PASS** |
| 3 | What are the escalation steps for a P1 production outage? | True | 1 | **PASS** |
| 4 | What should I check first when users cannot log in after a deployment? | False | 0 | **FAIL** |
| 5 | What is the best restaurant in Tokyo? | False | 0 | **PASS** |
| 6 | what is the | None | 0 | **PASS** |

## Details

### 1. How do I triage an authentication service incident?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: To triage an authentication service incident, follow these steps:  1. **Confirm the scope:** Check the auth service dashboard for the global error rate. If `auth_login_errors_total` is above 5% over the last 5 minutes, declare a P2 immediat

### 2. Which runbook should I follow for database connectivity issues?
- Status: **PASS**
- Grounded: `True` · Citations: `2`
- Answer preview: Based on the search results, you should follow the `database_connectivity_runbook.md` for database connectivity issues. This runbook is specifically designed to address issues related to database connectivity, such as applications logging "

### 3. What are the escalation steps for a P1 production outage?
- Status: **PASS**
- Grounded: `True` · Citations: `1`
- Answer preview: The escalation steps for a P1 production outage are as follows:  1. The primary on-call engineer is paged immediately. 2. If the primary on-call engineer does not acknowledge the incident within 8 minutes, the secondary on-call engineer is 

### 4. What should I check first when users cannot log in after a deployment?
- Status: **FAIL**
- Grounded: `False` · Citations: `0`
- Failure: grounded=False, expected=True
- Failure: expected citations when grounded
- Failure: citations missing expected source fragment(s): ['auth', 'deploy']
- Answer preview: Action: GlobalDataSource.search(query="What should I check first when users cannot log in after a deployment?")

### 5. What is the best restaurant in Tokyo?
- Status: **PASS**
- Grounded: `False` · Citations: `0`
- Answer preview: The model cannot find sufficient information to answer the question about the best restaurant in Tokyo. The search results provided do not contain any information related to restaurants in Tokyo.

### 6. what is the
- Status: **PASS**
- Grounded: `None` · Citations: `0`
- Answer preview: 
