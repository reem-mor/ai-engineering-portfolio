# Troubleshooting

## Empty User Message

`/api/chat` returns `empty_question` with a safe message.

## Unknown Service

Tools return structured `error` fields instead of crashing the backend.

## Missing Data File

Run:

```powershell
python scripts/validate_data.py
```

The script reports the missing CSV/JSON file or column.

## Bedrock Unavailable

Set `PITER_USE_BEDROCK=false` for local fallback, or keep fallback enabled while testing Bedrock.

## Missing Agent IDs

For `RAG_BACKEND=agent`, configure:

- `BEDROCK_AGENT_ID`
- `BEDROCK_AGENT_ALIAS_ID`

## Knowledge Base Not Synced

Sync `knowledge_base/` to S3, start ingestion, and test retrieval before the live demo.

## AWS CLI Pitfalls (PowerShell)

### KB retrieve returns empty results

The data source prefix must match both the S3 sync path **and** the Bedrock KB IAM
role `s3:GetObject` scope. If ingestion reports 403 on
`projects/piter-aiops/knowledge_base/*`, either:

- sync to `projects/piter-aiops/data/sample_documents/` (existing IAM scope), or
- extend `AmazonBedrockS3PolicyForKnowledgeBase_*` to include the `knowledge_base/`
  prefix.

After fixing prefix/IAM, run ingestion again.

### `ResourceNotFoundException` for `piter-*` Lambdas

Create the functions before updating action groups. Do not delete legacy `iiq-*`
Lambdas until the replacement `piter-*` functions exist.

### `add-permission` sourceArn validation error

PowerShell treats `$env:AWS_REGION:$ACCOUNT_ID` as a scoped variable. Build the ARN
explicitly:

```powershell
$AgentSourceArn = "arn:aws:bedrock:${env:AWS_REGION}:${AccountId}:agent/${AgentId}"
```

### `create-agent-version` not found

There is no `create-agent-version` AWS CLI command. Either:

- call `update-agent-alias` **without** `--routing-configuration` to snapshot a new
  version, or
- point a test alias at `DRAFT` (`TSTALIASID`).

### `invoke-agent` not found

`bedrock-agent-runtime` in AWS CLI 2.34 exposes `retrieve` and `retrieve-and-generate`,
not `invoke_agent`. Use:

```powershell
.\.venv\Scripts\python.exe scripts\agent_smoke_test.py
```

### Agent rename `ValidationException`

Agent names must match `([0-9a-zA-Z][_-]?){1,100}` — no spaces. Keep the existing
name (for example `incidentiq-triage-agent`) and update instructions only.

### Cannot delete enabled action groups

Disable first with `update-agent-action-group --action-group-state DISABLED`, or
repoint the group to the new Lambda with `update-agent-action-group`.

### `Failed to create OpenAPI 3 model` on action group update

Bedrock requires response bodies with `content.application/json.schema`, parameter
`description` fields, and API paths that match the Lambda handler defaults. The
legacy groups use `/correlate`, `/owner`, `/impact`, and `/similar` — not the
`piter-*` path names. Upload schemas to S3 and reference them:

```powershell
aws s3 cp action_groups/piter-recent-deployments/openapi_schema.yaml `
  s3://$Bucket/agent/iiq-correlate/openapi_schema.yaml
aws bedrock-agent update-agent-action-group `
  --agent-id $AGENT_ID --agent-version DRAFT --action-group-id S8LLMX7HKF `
  --action-group-name iiq-correlate `
  --action-group-executor "lambda=$LambdaArn" `
  --api-schema "s3=s3BucketName=$Bucket,s3ObjectKey=agent/iiq-correlate/openapi_schema.yaml" `
  --action-group-state ENABLED
```

### Corrected one-shot deploy

```powershell
.\scripts\aws_deploy_fix.ps1
```

## History

- `GET /api/history` returns the current process-local history.
- `DELETE /api/history` clears history.
- History resets when the Flask process restarts.
