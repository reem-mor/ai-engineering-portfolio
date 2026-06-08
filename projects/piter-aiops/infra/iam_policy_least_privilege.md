# IAM Least Privilege

Grant only what the demo needs.

## Flask / Demo Runtime

- `bedrock-agent-runtime:InvokeAgent` on the configured agent alias.
- Bedrock Knowledge Base retrieval permissions if direct KB fallback is enabled.

## Knowledge Base S3

- `s3:GetObject`
- `s3:ListBucket`

Scope resources to:

- `arn:aws:s3:::<bucket-name>`
- `arn:aws:s3:::<bucket-name>/projects/piter-aiops/knowledge_base/*`

## Lambda Action Groups

- Bedrock Agent role can invoke the specific action-group Lambda ARNs.
- Lambda execution role can write CloudWatch Logs.

Avoid administrator access as the final project posture.
