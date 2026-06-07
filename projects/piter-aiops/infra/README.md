# IAM policy template

Replace placeholders in `iam_policy.json` before attaching to an EC2 instance profile or task role:

- `REGION`, `ACCOUNT_ID`, `KB_ID`, `S3_BUCKET_NAME`

Ensure `BEDROCK_MODEL_ARN` in `.env` matches a `Resource` under **BedrockInvokeInferenceProfile** (inference profile ARN or regional foundation-model ARN). If you use a different model than Nova Lite, add its ARN to that statement.
