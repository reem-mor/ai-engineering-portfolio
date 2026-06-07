# Bedrock Agent Smoke Test Results

- **Run at:** 2026-06-07 15:18:34 UTC
- **Backend / ref:** `HH4YGSLZUE/O2EM03R4R3`
- **Score:** 4/7 PASS

| ID | Status | Grounded | Citations | Latency ms |
|----|--------|----------|-----------|------------|
| 1 | PASS | True | 5 | 13994 |
| 2 | FAIL | False | 0 | 3477 |
| 3 | FAIL | False | 0 | 3328 |
| 4 | FAIL | False | 0 | 3551 |
| 5 | PASS | True | 4 | 4902 |
| 6 | PASS | False | 0 | 2326 |
| 7 | PASS | — | — | — |

### FAIL #2: API 5xx rate is above 2% on checkout — what should I check?
- expected grounded answer but got no citations

### FAIL #3: Queue lag is above 30 seconds — what should I do?
- expected grounded answer but got no citations
- answer missing keywords: ['worker', 'scale', 'dead-letter', 'DLQ']

### FAIL #4: Users cannot log in after deployment — what should I check?
- expected grounded answer but got no citations
- answer missing keywords: ['health', 'JWT', 'TOKEN_ISSUER', 'rollback']
