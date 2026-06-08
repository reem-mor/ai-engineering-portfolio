# PITER AWS Phase 1 — Environment and Config Check

**Audit date:** 2026-06-08  
**Scope:** `projects/piter-aiops` (read-only)  
**Auditor:** Controlled AWS readiness verification (no mutations)

## 1. Working directory

```
C:\dev\amdocs-ai-course\projects\piter-aiops
```

## 2. Git branch

```
main
```

## 3. Git status

```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## 4. AWS profile in use

| Source | Value |
|--------|-------|
| Project `.env` / `Config` | `reemmor` |
| Shell `AWS_PROFILE` (during audit) | Set explicitly to `reemmor` for CLI calls |
| Default CLI profile (no env) | `us-east-1` region from `aws configure get region` |

## 5. AWS region in use

```
us-east-1
```

## 6. Relevant environment variables (names only; values masked)

| Variable | Status | Notes |
|----------|--------|-------|
| `PITER_AWS_REGION` | Set | `us-east-1` |
| `AWS_PROFILE` | Set in `.env` | `reemmor` |
| `RAG_BACKEND` | Set | **`retrieve_and_generate`** (live demo path) |
| `USE_BEDROCK` / `PITER_USE_BEDROCK` | Set | `true` |
| `PITER_BEDROCK_AGENT_ID` | Set | `HH4Y…ZUE` |
| `PITER_BEDROCK_AGENT_ALIAS_ID` | Set | `O2EM…4R3` |
| `PITER_KNOWLEDGE_BASE_ID` | Not set | App uses `PITER_BEDROCK_KB_ID` instead |
| `PITER_BEDROCK_KB_ID` | Set | `RBTJ…IG9` |
| `PITER_GUARDRAIL_ID` | **Unset** | Bedrock guardrail exists in account but not wired locally |
| `PITER_GUARDRAIL_VERSION` | **Unset** | — |
| `PITER_NOTIFICATION_MODE` | Set | `live` |
| `PITER_SNS_TOPIC_ARN` | Set | `arn:aws:sns:us-east-1:329***579:piter-aiops-escalation` |
| `PITER_SES_SENDER_EMAIL` | Set | `fo***@gmail.com` (masked) |

### Additional config observed (not in original list)

| Variable | Status |
|----------|--------|
| `PITER_BEDROCK_DATA_SOURCE_ID` | Set (`YICX…WOG`) |
| `PITER_S3_BUCKET` | Set (`reem…331`) |
| `PITER_ENABLE_LIVE_DISPATCH` | Set (`true`) |
| `PITER_NOTIFICATION_REQUIRE_CONFIRMATION` | Set (`true`) |
| `PITER_NOTIFICATION_CONFIRMATION_TOKEN` | Set (value not recorded) |
| `PITER_NOTIFICATION_ALLOWLIST` | Set (SMS + email endpoints; masked) |

## Findings

1. **Live demo path** uses `RAG_BACKEND=retrieve_and_generate`, not `agent`. Agent IDs are still configured for `invoke_agent` verification.
2. **Guardrail env vars** are absent; app relies on `app/guardrails.py` operator rules.
3. **Notification mode is `live`** with confirmation gates enabled — appropriate for controlled demo, but SMS sandbox constraints apply (see Phase 9).

## Commands run (read-only)

```powershell
git -C C:\dev\amdocs-ai-course branch --show-current
git -C C:\dev\amdocs-ai-course status
# Config loaded via project venv: Config.from_env()
```
