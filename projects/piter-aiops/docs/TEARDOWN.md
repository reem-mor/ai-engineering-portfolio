# Teardown checklist (on go-ahead after demo)

**Account:** `329597159579` · **Region:** `us-east-1` · **Profile:** `reemmor`  
**Tags:** `Project=piter-aiops`, `Owner=reemmor`

Do **not** delete until you have exported screenshots and graded submission artifacts.

## Resources created or used by this upgrade

| Resource | ID / name | Rough cost |
|----------|-----------|------------|
| Knowledge Base | `RBTJM6NIG9` (`PITER AiOps-course-kb`) | OpenSearch Serverless vector store (largest cost) |
| Data source | `YICXAB6WOG` | Included in KB |
| Bedrock Agent | `HH4YGSLZUE` | Per `invoke_agent` token + tool calls |
| Agent alias | `live` (check `.env` `BEDROCK_AGENT_ALIAS_ID`) | No separate charge |
| Lambda | `PITER AiOps-actions`, `iiq-correlate`, `iiq-context`, `iiq-similar` | Free tier / per-invoke |
| IAM roles | `PITER AiOps-lambda-role`, `PITER AiOps-agent-role` | Free |
| S3 prefix | `s3://reem-amdocs-ai-artifacts-3331/projects/piter-aiops/` + `agent/` | Storage pennies |
| Cognito (Path A) | Only if you created a pool for MCP | Free tier |
| AgentCore Gateway | Only if created manually | Usage-based |
| EC2 (if deployed) | Course t3.micro | Hourly while running |

## Delete order (safest)

1. Delete Bedrock Agent aliases, then agent `HH4YGSLZUE`
2. Delete action groups (automatic with agent) and Lambdas `iiq-*`, `PITER AiOps-actions`
3. Delete KB `RBTJM6NIG9` and associated OpenSearch Serverless collection (console)
4. Remove S3 objects under project prefix (optional; keep bucket if shared)
5. Delete IAM roles `PITER AiOps-agent-role`, `PITER AiOps-lambda-role` after detaching policies
6. Terminate EC2 instance if used for public demo

## Commands (examples)

```powershell
aws bedrock-agent delete-agent-alias --agent-id HH4YGSLZUE --agent-alias-id <ALIAS_ID> --profile reemmor
aws bedrock-agent delete-agent --agent-id HH4YGSLZUE --profile reemmor
aws lambda delete-function --function-name iiq-correlate --profile reemmor
# repeat for iiq-context, iiq-similar, PITER AiOps-actions
```

KB and vector store deletion must be done in the Bedrock / OpenSearch consoles per course cleanup guide.

## Cleanup note

After deletion, update this file with date and confirmation that billing alarms show no ongoing Bedrock/OS charges.
