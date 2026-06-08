# PITER AWS Infrastructure Audit (Read-Only)

**Region:** us-east-1 | **Mutations:** none

## Resource summary

| Resource | ID / name | Purpose | Status | Env var |
|----------|-----------|---------|--------|---------|
| S3 bucket | `reem-amdocs-ai-artifacts-3331` | KB corpus, agent schemas | Active | `PITER_S3_BUCKET` |
| S3 prefix | `projects/piter-aiops/data/sample_documents/` | KB data source | ~28 objects | `PITER_S3_PREFIX` |
| Bedrock KB | `RBTJM6NIG9` | RAG corpus | Active | `PITER_BEDROCK_KB_ID` |
| KB data source | `YICXAB6WOG` | S3 connector | AVAILABLE | `PITER_BEDROCK_DATA_SOURCE_ID` |
| Bedrock Agent | `HH4YGSLZUE` | Agent orchestration | PREPARED | `PITER_BEDROCK_AGENT_ID` |
| Agent alias | `O2EM03R4R3` (`live`) | Stable invoke | PREPARED v3 | `PITER_BEDROCK_AGENT_ALIAS_ID` |
| Lambda | `iiq-correlate`, `iiq-context`, `iiq-similar` | Action groups | Active python3.12 | — |
| SNS topic | `piter-aiops-escalation` (per .env) | Escalation | Configured locally | `PITER_SNS_TOPIC_ARN` |
| SES | sender + config set in .env | Email escalation | Configured locally | `PITER_SES_*` |
| EC2 | Terminated per `docs/cleanup_log.md` | Was public demo | **Terminated** | — |

## IAM

- `infra/iam_policy_ec2_resolved.json` — Haiku inference profile ARN
- Legacy S3 prefixes in `infra/bedrock_kb_s3_policy*.json` include old project paths — low risk if KB only uses piter-aiops prefix

## Risks

| Risk | Severity | Fix |
|------|----------|-----|
| Agent branded IncidentIQ | Low (cosmetic) | Rename in console |
| Missing piter-escalation Lambda | Medium | Deploy + attach |
| Legacy S3 ARNs in IAM templates | Low | Update JSON templates |
| Live notification mode in dev .env | Medium | Use mock for shared clones |

## EC2

Instance terminated — no start recommended unless public URL demo required. Prefer local Docker + Bedrock.

## Commands used (read-only)

- `aws bedrock-agent get-agent`
- `aws bedrock-agent list-agent-aliases`
- `aws bedrock-agent get-knowledge-base`
- `aws bedrock-agent list-data-sources`
- `aws bedrock-agent list-agent-knowledge-bases`
- `aws bedrock-agent list-agent-action-groups`
- `aws lambda list-functions`
- `aws s3 ls` (prefix)
