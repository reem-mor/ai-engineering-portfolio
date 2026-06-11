# Bedrock Flows Demo

Amazon Bedrock **Flows** are versioned, multi-step prompt pipelines. You define **nodes** (Input, Prompt, Output, Knowledge Base, Condition, …) and **connections** between them, then invoke the flow through an **alias**.

This folder implements a minimal summarizer:

```mermaid
flowchart LR
  Input[FlowInput] --> Prompt[SummarizeText]
  Prompt --> Output[FlowOutput]
```

---

## Prerequisites

1. **AWS account** with Bedrock model access (enable `amazon.nova-lite-v1:0` or your chosen model in the Bedrock console).
2. **IAM execution role** for Bedrock Flows — see [Create a service role for Flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-permissions.html).
3. **AWS credentials** configured (`aws configure` or `AWS_PROFILE`).

---

## Files

| File | Purpose |
|------|---------|
| `flow_definition.json` | Node/connection definition (Input → Prompt → Output) |
| `create_flow.py` | Creates flow, prepares, versions, creates `latest` alias |
| `invoke_flow.py` | Invokes flow alias with sample or CLI text |

---

## Setup

From the lesson root:

```powershell
cd lectures\09_flows_bedrock_n8n
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

- `BEDROCK_FLOWS_EXECUTION_ROLE_ARN` — your Flows service role ARN
- `AWS_REGION` — region where Bedrock is enabled (e.g. `us-east-1`)
- `BEDROCK_MODEL_ID` — model enabled in your account

---

## Run

### 1. Create the flow (one-time)

```powershell
python bedrock_flows\create_flow.py
```

Copy the printed `BEDROCK_FLOW_ID` and `BEDROCK_FLOW_ALIAS_ID` into `.env`.

### 2. Invoke the flow

```powershell
python bedrock_flows\invoke_flow.py
```

Optional custom input:

```powershell
python bedrock_flows\invoke_flow.py "Your long paragraph to summarize here."
```

### 3. Console alternative

You can also build the same flow in **Amazon Bedrock → Flows** using the visual designer. Export the flow ID and alias from the console into `.env` and skip `create_flow.py`.

---

## API clients

| Operation | Boto3 client |
|-----------|--------------|
| `create_flow`, `prepare_flow`, `create_flow_version`, `create_flow_alias` | `bedrock-agent` |
| `invoke_flow` | `bedrock-agent-runtime` |

`invoke_flow` returns a **response stream** — collect events until `flowCompletionEvent.completionReason` is `SUCCESS`, then read `flowOutputEvent`.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `AccessDeniedException` on create | Execution role missing `bedrock:InvokeModel` and Flows trust policy |
| Model not found | Enable the model in Bedrock console → Model access |
| `invoke_flow` not on client | Upgrade boto3 (`pip install -U boto3`); use `bedrock-agent-runtime` |
| Flow not prepared | Run `prepare_flow` or use `create_flow.py` which calls it |

---

## References

- [Flows code samples (AWS)](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-code-ex.html)
- [Node types for flows](https://docs.aws.amazon.com/bedrock/latest/userguide/flows-nodes.html)
