# PITER AiOps Demo Script

Use this for a 5-7 minute mid-project live demo.

## 0. Pre-demo check

Run these before presenting:

```powershell
cd C:\dev\amdocs-ai-course\projects\piter-aiops
python scripts/verify_live_demo.py
docker compose up -d
```

Open:

- Dashboard: `http://localhost:8080/`
- Health: `http://localhost:8080/api/health`

## 1. Opening - 30 seconds

PITER AiOps is an AI incident response assistant for NOC, SRE, DevOps, and operations teams.

PITER means:

- Priority
- Investigation
- Triage
- Escalation
- Resolution

The goal is to reduce time-to-understand by combining runbooks, incident history, service ownership, deployment data, and Bedrock Agent reasoning.

## 2. Architecture - 45 seconds

Explain the runtime path:

```text
React dashboard
-> Flask API
-> boto3 Bedrock Agent Runtime
-> Bedrock Agent
-> Bedrock Knowledge Base
-> Action Group / MCP-style tools
-> Structured PITER response
-> Memory and chat history
```

Point out that AWS success is real when configured, and local fallback is honest when AWS is unavailable.

## 3. Incident analysis - 90 seconds

Use the dashboard incident workflow or call:

```text
Analyze this alert: high error rate on auth-service in production after deployment.
```

Show:

- PITER structured answer
- Priority and business impact
- Investigation steps
- Retrieved context / citations
- Tool results

## 4. Tool results - 60 seconds

Explain the four tool contracts:

- `get_recent_deployments(service, environment)`
- `get_service_context(service)`
- `find_similar_incidents(service, symptom, severity)`
- `get_escalation_recommendation(service, priority, business_impact)`

Mention that the same business logic is shared by Flask, MCP-style local tooling, and Bedrock Action Group handlers.

## 5. Memory and follow-up - 60 seconds

Ask:

```text
Who should I escalate this incident to?
```

Then ask:

```text
What was my previous question?
```

Show session memory, chat history, and the saved `session_id`.

## 6. Safety and fallback - 45 seconds

Show Settings/Architecture and explain:

- `.env` controls Bedrock vs local fallback.
- AWS credentials are stored in the AWS CLI profile, not committed.
- Bedrock failures return a clear error or local fallback, not fake success.
- Escalation notifications are mock/preview by default.

## 7. Closing - 30 seconds

Close with:

PITER AiOps demonstrates Flask, React, Bedrock Agent Runtime through `boto3`, Knowledge Base RAG, action-group/MCP-style tools, Pandas/CSV/JSON data processing, memory, chat history, Docker, tests, and a clean demo-ready repository.

## Recommended demo questions

```text
What should I check when users cannot log in after the latest deployment?

Analyze this alert: high error rate on auth-service in production after deployment.

Who should I escalate this incident to?

Are there similar incidents from the past?

What is the business impact of this issue?

What was my previous question?

Based on the previous incident, what should I do next?
```
