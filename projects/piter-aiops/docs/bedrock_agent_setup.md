# Bedrock Agent — Setup Walkthrough

End-to-end steps to create a **managed Amazon Bedrock Agent** that uses your existing Knowledge Base. The Flask app calls `invoke_agent` instead of direct `RetrieveAndGenerate`.

> Reuse the KB from [`bedrock_kb_setup.md`](bedrock_kb_setup.md). You do not need a second OpenSearch collection.

---

## Prerequisites

- Knowledge Base created and synced (`BEDROCK_KB_ID` in `.env`)
- Model access granted (same inference profile as `BEDROCK_MODEL_ARN`)
- IAM permissions for `bedrock-agent:*` (setup) and `bedrock:InvokeAgent` (runtime)

---

## Option A — Automated script

From project root:

```powershell
cd projects\piter-aiops
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Fill BEDROCK_KB_ID, BEDROCK_MODEL_ARN, FLASK_SECRET_KEY, etc.

python scripts/setup_bedrock_agent.py --dry-run
python scripts/setup_bedrock_agent.py
```

Copy the printed `BEDROCK_AGENT_ID` and `BEDROCK_AGENT_ALIAS_ID` into `.env`:

```env
RAG_BACKEND=agent
BEDROCK_AGENT_ID=XXXXXXXXXX
BEDROCK_AGENT_ALIAS_ID=YYYYYYYYYY
```

---

## Option B — AWS Console

1. **Bedrock → Agents → Create agent**
   - Name: `PITER AiOps-noc-agent`
   - Model: same inference profile as `.env` (`BEDROCK_MODEL_ARN`)
   - Instructions: NOC triage persona (see `AGENT_INSTRUCTION` in [`app/bedrock_agent_client.py`](../app/bedrock_agent_client.py))

2. **Add knowledge base**
   - Select existing KB (`BEDROCK_KB_ID`)
   - Enable retrieval

3. **Prepare agent** (required before alias works)

4. **Create alias** (e.g. `live`) — copy Agent ID and Alias ID to `.env`

5. **Test in console** — ask: *"How do I triage an authentication service incident?"*

📸 Screenshot for submission: `screenshots/20_bedrock_agent_overview.png`

---

## Runtime IAM (EC2 / local)

Add to your instance profile or user policy ([`infra/iam_policy.json`](../infra/iam_policy.json)):

```json
{
  "Sid": "BedrockInvokeAgent",
  "Effect": "Allow",
  "Action": "bedrock:InvokeAgent",
  "Resource": [
    "arn:aws:bedrock:REGION:ACCOUNT_ID:agent/AGENT_ID",
    "arn:aws:bedrock:REGION:ACCOUNT_ID:agent-alias/AGENT_ID/*"
  ]
}
```

---

## Fallback mode

If the agent is not provisioned yet, set:

```env
RAG_BACKEND=retrieve_and_generate
```

The app uses direct KB `RetrieveAndGenerate` ([`app/bedrock_client.py`](../app/bedrock_client.py)) without agent IDs.

---

## Verify

```powershell
pytest tests/test_bedrock_agent_client.py -q
python scripts/agent_smoke_test.py
```

Expected: grounded answers with citations for runbook questions from [`evaluation/test_questions.json`](../evaluation/test_questions.json).

For action group ops tools, see [`bedrock_action_group_setup.md`](bedrock_action_group_setup.md).
