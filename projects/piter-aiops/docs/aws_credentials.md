# AWS credentials and configuration — PITER AiOps

Two layers: **AWS auth** (bearer token or CLI profile) and **Bedrock resource IDs / app secrets** in project `.env`.

| What | Where | Never put here |
|------|--------|----------------|
| Bedrock short-term API key | Windows env `AWS_BEARER_TOKEN_BEDROCK` or `.env` (gitignored) | git / README |
| AWS access key + secret | `~/.aws/credentials` | `.env` (long-lived keys) |
| Profile name | `.env` → `AWS_PROFILE` | source code |
| KB / Agent IDs, model ARN, S3 | `.env` → `PITER_*` | git / README |
| Flask CSRF signing | `.env` → `PITER_FLASK_SECRET_KEY` | git |

**Not used by this app:** `c:/dev/amdocs-ai-course/.env` (course repo root). Edit only `projects/piter-aiops/.env`.

Loader: [`app/config.py`](../app/config.py) — `PITER_*` preferred; legacy unprefixed names still supported (see [`.env.example`](../.env.example)).

Requires **boto3 >= 1.39.0** ([`requirements.txt`](../requirements.txt)) for bearer-token auth.

## 1. AWS access keys (`~/.aws/credentials`)

```powershell
aws configure --profile reemmor
```

Or edit `C:\Users\<you>\.aws\credentials`:

```ini
[reemmor]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

Optional `~/.aws/config`:

```ini
[profile reemmor]
region = us-east-1
output = json
```

In project `.env`:

```env
AWS_PROFILE=reemmor
```

Verify (no secrets printed):

```powershell
aws sts get-caller-identity --profile reemmor
python scripts/verify_credentials.py
```

## 1b. Bedrock short-term API key (Path C — bearer token)

For **invoke_agent** and **retrieve** without `~/.aws/credentials`. Generate in Bedrock console → **API keys** → **Short-term API keys** (max 12 hours, region-specific).

Set the token (do not commit):

```powershell
# Windows user env (persists across sessions)
setx AWS_BEARER_TOKEN_BEDROCK "bedrock-api-key-..."
# Open a new terminal after setx
```

Or in project `.env` (gitignored):

```env
AWS_BEARER_TOKEN_BEDROCK=bedrock-api-key-...
# AWS_PROFILE=reemmor   # comment out to avoid profile/bearer conflict
```

boto3 reads `AWS_BEARER_TOKEN_BEDROCK` automatically — no app code changes. Requires boto3 >= 1.39.0.

Verify (no secrets printed):

```powershell
if ($env:AWS_BEARER_TOKEN_BEDROCK) { "Bearer token: set" } else { "Bearer token: NOT SET" }
python scripts/agent_smoke_test.py
```

**Bearer covers:** `bedrock-agent-runtime` (`invoke_agent`, `retrieve`, RetrieveAndGenerate).

**Still needs IAM profile:** S3 upload, `bedrock-agent` control plane, SNS/SES notifications. For live notifications, keep `AWS_PROFILE` and valid `~/.aws/credentials` in addition to bearer for Bedrock RAG.

Docker Compose passes `AWS_BEARER_TOKEN_BEDROCK` from host env or `.env` — see [`docker-compose.yml`](../docker-compose.yml).

## 2. Project `.env` (resource IDs + Flask secret)

```powershell
cd projects/piter-aiops
copy .env.example .env
```

### Required when `PITER_USE_BEDROCK=true`

| Variable | Purpose |
|----------|---------|
| `PITER_AWS_REGION` | Bedrock region |
| `PITER_BEDROCK_KB_ID` | Knowledge Base ID |
| `PITER_BEDROCK_MODEL_ARN` | Inference profile or model ARN |
| `PITER_FLASK_SECRET_KEY` | CSRF signing — `python -c "import secrets; print(secrets.token_hex(32))"` |

### Required when `RAG_BACKEND=agent`

| Variable | Purpose |
|----------|---------|
| `PITER_BEDROCK_AGENT_ID` | Agent ID |
| `PITER_BEDROCK_AGENT_ALIAS_ID` | Agent alias |

### Offline mode

```env
PITER_USE_BEDROCK=false
```

No AWS keys required.

## 3. Local Python / pytest

1. `cd projects/piter-aiops`
2. `pip install -r requirements-dev.txt`
3. Keys: `~/.aws` + `AWS_PROFILE` in `.env`
4. IDs: `PITER_*` in `.env`
5. Tests mock Bedrock — no AWS calls in `pytest`

## 4. Docker Compose (local)

[`docker-compose.yml`](../docker-compose.yml):

- `env_file: .env` — loads `PITER_*`, `AWS_PROFILE`, and `AWS_BEARER_TOKEN_BEDROCK`
- `AWS_BEARER_TOKEN_BEDROCK` — interpolated from host env when not in `.env`
- `~/.aws:/home/app/.aws:ro` — mounts host credentials for IAM profile auth

```powershell
docker compose up --build
```

Set `PITER_USE_BEDROCK=true` in `.env` for live Bedrock.

## 5. EC2 demo

- **No** `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` in server `.env`
- EC2 **IAM instance profile** supplies credentials to boto3 on the host
- Server `.env` only: `PITER_BEDROCK_*` IDs, `PITER_FLASK_SECRET_KEY`, `RAG_BACKEND`, `FLASK_ENV=production`

See [`infra/ec2_user_data_demo.sh`](../infra/ec2_user_data_demo.sh).

## Setup scripts vs runtime

| Context | AWS auth | Config |
|---------|----------|--------|
| Flask / Docker (local) | `AWS_BEARER_TOKEN_BEDROCK` and/or `~/.aws` + `AWS_PROFILE` | `projects/piter-aiops/.env` |
| Flask on EC2 | IAM instance profile | `/home/ec2-user/.env` |
| `scripts/setup_*.py` (laptop) | `~/.aws` | `.env` for IDs / bucket |
| pytest | Mocked | `tests/conftest.py` |
| Cursor MCP (Path C) | `~/.aws` + `AWS_PROFILE=reemmor` in `.cursor/mcp.json` | [`config/mcp.json.example`](../config/mcp.json.example) · [`docs/MCP_PATH.md`](MCP_PATH.md) |
