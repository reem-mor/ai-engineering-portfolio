# PITER AWS Phase 2 — Identity and Region Verification

**Audit date:** 2026-06-08  
**Profile:** `reemmor`  
**Region:** `us-east-1`

## Commands run (read-only)

```powershell
# Purpose: verify caller identity
aws sts get-caller-identity --output json

# Purpose: verify configured region
aws configure get region
```

## Results

| Field | Value (masked where appropriate) |
|-------|----------------------------------|
| Account ID | `329***579` (full: 329597159579) |
| Principal type | IAM user |
| User ID | `AIDAUZPMFRCNX3TC6MU43` |
| ARN | `arn:aws:iam::329597159579:user/admin-reem` |
| Region | `us-east-1` |
| Profile | `reemmor` |

## Root/admin assumptions

- **Not required.** Caller is a standard IAM user (`admin-reem`), not root.
- Read-only Bedrock, Lambda, S3, SNS, SES, EC2, and CloudWatch APIs succeeded with this identity.
- No evidence that Organization SCPs blocked read operations during this audit.

## Risk notes

- User-named admin IAM user has broad permissions (inferred from successful cross-service reads). Least-privilege review recommended before production, but acceptable for course/demo account.
