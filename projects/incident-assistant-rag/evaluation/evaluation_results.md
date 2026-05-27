# RAG Evaluation Results

Mode: Live (OpenAI)
Passed: 5/5

## Test 1 - PASS

Question: What should I check when users cannot log in after deployment?

Confidence: medium

Used context: True

Actual sources: ['auth_service_runbook.md', 'deployment_failure_sop.docx', 'incident_examples.csv']

Missing keywords: []

When users cannot log in after deployment, you should check the following:

1. Check the auth-service health endpoint.
2. Check auth-service logs for authentication errors.
3. Check recent deployments and release notes.
4. Verify environment variables related to JWT_SECRET, AUTH_DB_URL, and TOKEN_ISSUER.
5. Check database connectivity from the auth-service.
6. Confirm that token expiration settings were not changed.

## Test 2 - PASS

Question: What should I do if payment requests are slow and users report timeout?

Confidence: medium

Used context: True

Actual sources: ['incident_examples.csv', 'monitoring_alerts.md', 'payment_service_latency.txt']

Missing keywords: []

If payment requests are slow and users report timeout, you should take the following actions:

1. Check payment-service logs for timeout errors.
2. Check the external provider status page for any reported issues.
3. Check the queue size and retry backlog.
4. Check database latency for payment status writes.
5. Verify that duplicate charge protection is enabled.
6. If the situation is critical, escalate to the payments team and other relevant teams. 

Make sure to avoid manually retrying payments without checking for duplicate charge risk.

## Test 3 - PASS

Question: How should I investigate database locks?

Confidence: medium

Used context: True

Actual sources: ['database_locks_runbook.pdf', 'incident_examples.csv', 'monitoring_alerts.md']

Missing keywords: []

To investigate database locks, follow these steps:

1. Check active sessions.
2. Identify blocked queries.
3. Identify the blocking process.
4. Check whether a migration or long-running transaction started recently.
5. Review database connection pool usage.

If blocking queries affect production users or if the blocking process is unknown, escalate to the DBA team.

## Test 4 - PASS

Question: Many users cannot log in after the latest production deployment.

Confidence: medium

Used context: True

Actual sources: ['auth_service_runbook.md', 'deployment_failure_sop.docx', 'incident_examples.csv']

Missing keywords: []

Many users cannot log in after the latest production deployment.

## Test 5 - PASS

Question: What is the best restaurant in Tokyo?

Confidence: none

Used context: False

Actual sources: []

Missing keywords: []

The knowledge base does not contain enough information to answer this question.
