# Bedrock Agent Smoke Test Results

- **Run at:** 2026-06-04 07:56:35 UTC
- **Backend / ref:** `HH4YGSLZUE/O2EM03R4R3`
- **Score:** 5/7 PASS

| ID | Status | Grounded | Citations | Latency ms |
|----|--------|----------|-----------|------------|
| 1 | PASS | True | 4 | 9948 |
| 2 | FAIL | False | 0 | 4718 |
| 3 | FAIL | False | 0 | 4899 |
| 4 | PASS | True | 9 | 35171 |
| 5 | PASS | True | 3 | 6513 |
| 6 | PASS | False | 0 | 4644 |
| 7 | PASS | — | — | — |

### FAIL #2: API 5xx rate is above 2% on checkout — what should I check?
- expected grounded answer but got no citations

### FAIL #3: Queue lag is above 30 seconds — what should I do?
- expected grounded answer but got no citations
- answer missing keywords: ['worker', 'scale', 'dead-letter', 'DLQ']
