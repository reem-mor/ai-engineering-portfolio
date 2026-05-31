# Cleanup log — 2026-05-31

Resources created during the Cursor workflow implementation and removed the same day.

## Deleted

| Resource | ID / name | Action |
|----------|-----------|--------|
| EC2 instance | `i-0ff0a902311a5943b` (`incident-rag-demo`) | Terminated |
| Security group | `sg-052717984128f7617` (`incident-rag-sg`) | Deleted |
| IAM instance profile | `incident-rag-ec2-profile` | Deleted |
| IAM role | `incident-rag-ec2-role` | Deleted (inline policy removed first) |

## Retained (shared / reusable)

| Resource | Notes |
|----------|--------|
| Bedrock KB `RBTJM6NIG9` | Pre-existing course KB; ingestion refreshed with bedrock corpus |
| S3 bucket `reem-amdocs-ai-artifacts-3331` | Source documents; not emptied |
| ECR repo `incident-rag-bedrock:demo` | Image kept for future deploys (~small storage cost) |

## Public URL used during validation (now offline)

`http://ec2-13-222-142-122.compute-1.amazonaws.com/` — instance terminated after `/health` check.

For assignment screenshots, relaunch EC2 using [`ec2_deployment.md`](ec2_deployment.md) and [`infra/ec2_user_data_ecr.sh`](../infra/ec2_user_data_ecr.sh), then tear down again per [`cleanup_checklist.md`](cleanup_checklist.md).
