# Bedrock Agent Smoke Test Results

- **Run at:** 2026-06-03 10:49:46 UTC
- **Backend / ref:** `XXXXXXXXXX/YYYYYYYYYY`
- **Score:** 1/7 PASS

| ID | Status | Grounded | Citations | Latency ms |
|----|--------|----------|-----------|------------|
| 1 | FAIL | — | — | — |
| 2 | FAIL | — | — | — |
| 3 | FAIL | — | — | — |
| 4 | FAIL | — | — | — |
| 5 | FAIL | — | — | — |
| 6 | FAIL | — | — | — |
| 7 | PASS | — | — | — |

### FAIL #1: Postgres CPU is 95% on prod-db-1 — what is the runbook?
- BedrockError: Could not reach AWS Bedrock. Check network or credentials. (botocore_error)

### FAIL #2: API 5xx rate is above 2% on checkout — what should I check?
- BedrockError: Could not reach AWS Bedrock. Check network or credentials. (botocore_error)

### FAIL #3: Queue lag is above 30 seconds — what should I do?
- BedrockError: Could not reach AWS Bedrock. Check network or credentials. (botocore_error)

### FAIL #4: Users cannot log in after deployment — what should I check?
- BedrockError: Could not reach AWS Bedrock. Check network or credentials. (botocore_error)

### FAIL #5: How do I decide if an alert should be resolved at Tier 1 or escalated?
- BedrockError: Could not reach AWS Bedrock. Check network or credentials. (botocore_error)

### FAIL #6: What is the best restaurant in Tokyo?
- BedrockError: Could not reach AWS Bedrock. Check network or credentials. (botocore_error)
