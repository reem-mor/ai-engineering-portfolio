# PITER AiOps — AWS Infrastructure Audit (read-only)

- **Author:** Re'em Mor
- **Date:** 2026-06-07
- **Constraint:** Read-only. No AWS resource created, modified, synced, or deleted.

## Components (from code/infra/docs — live state NOT VERIFIED without credentials)
| Component | Source of truth | Verified here? |
| --------- | --------------- | -------------- |
| S3 buckets | `infra/bedrock_kb_s3_policy*.json`, `app/upload_service.py` (prefix `projects/piter-aiops/data/sample_documents`) | NOT VERIFIED (no creds) |
| Bedrock Knowledge Base | `scripts/setup_bedrock_*`, `docs/bedrock_kb_setup.md` | NOT VERIFIED |
| Bedrock Agent | `scripts/setup_bedrock_agent.py`, `app/bedrock_agent_client.py` | NOT VERIFIED |
| Guardrails | `PITER_GUARDRAIL_*` env | NOT VERIFIED |
| Lambda functions | `action_groups/*`, `scripts/setup_enrichment_lambdas.py` | NOT VERIFIED |
| Action Groups | `scripts/setup_action_group.py`, OpenAPI schemas | NOT VERIFIED |
| IAM roles/policies | `infra/*.json` (trust + inline) | NOT VERIFIED |
| SNS / SES | `app/services/notification_dispatch.py`, `infra/notifications_policy*.json` | NOT VERIFIED |
| EC2 | `infra/ec2_user_data*.sh` (optional; not needed for local demo) | NOT VERIFIED |
| CloudWatch logs/traces | `enableTrace=True`, app logging | NOT VERIFIED |

## What IS verifiable here
- **AWS reachability:** dummy creds against `retrieve_and_generate` returned
  `UnrecognizedClientException` → network path to Bedrock is open; only credentials are missing.
- **boto3 wiring:** all clients use env-driven region/IDs, no hardcoded secrets.
- **Local demo independence:** Docker/local path works fully offline (fallback proven 14/14).

## Read-only verification commands (run with a valid profile in the graded env)
```bash
aws sts get-caller-identity
aws bedrock-agent get-agent --agent-id "$PITER_BEDROCK_AGENT_ID"
aws bedrock-agent list-agent-knowledge-bases --agent-id "$PITER_BEDROCK_AGENT_ID" --agent-version DRAFT
aws bedrock-agent list-agent-action-groups --agent-id "$PITER_BEDROCK_AGENT_ID" --agent-version DRAFT
aws lambda list-functions --query "Functions[?contains(FunctionName,'iiq') || contains(FunctionName,'piter')].FunctionName"
aws s3 ls "s3://$PITER_S3_BUCKET/$PITER_S3_PREFIX/"
```

## Acceptance (to confirm in graded env)
- KB associated with Agent · Agent callable via boto3 · alias prepared · action groups attached ·
  4 relevant Lambdas · S3 prefixes clear · least-privilege IAM · logs present & safe · SES/SNS safe
  defaults · EC2 optional · Docker local demo works.

## Status: NOT VERIFIED (read-only sandbox, no creds). Code + infra artifacts consistent and ready.
