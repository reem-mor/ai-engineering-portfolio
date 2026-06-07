# MCP integration path (Phase 3)

## Decision

| Path | Status | Role |
|------|--------|------|
| **B — Bedrock action groups** | **Deployed** | Reliable tool path for `invoke_agent` (iiq-correlate, iiq-context, iiq-similar) |
| **A — AgentCore Gateway (MCP)** | **Documented / probe** | Same Lambdas exposed as MCP tools with Cognito OAuth when account supports it |
| **C — Cursor IDE (developer)** | **Configured** | AWS + Bedrock KB + docs + Playwright for local agent assistance (not used by `invoke_agent`) |

The Bedrock Agent **always** uses action groups for enrichment during triage. Path A adds an MCP-native front for external clients (IDE, other agents) over the same Lambda implementations.

## Cost estimate (demo)

- **Cognito user pool**: free tier for small user counts
- **Lambda enrichment**: pay per invoke (negligible for course demo)
- **AgentCore Gateway**: usage-based; confirm in AWS console before enabling in production

## Path B — Action groups (implemented)

Deploy:

```powershell
cd projects/piter-aiops
python scripts/setup_enrichment_lambdas.py --agent-id HH4YGSLZUE
python scripts/setup_action_group.py --agent-id HH4YGSLZUE
```

| Action group | Lambda | Operations |
|--------------|--------|------------|
| `iiq-correlate` | `iiq-correlate` | `POST /correlate` |
| `iiq-context` | `iiq-context` | `POST /owner`, `POST /impact` |
| `iiq-similar` | `iiq-similar` | `POST /similar` |
| `PITER AiOps-ops` | `PITER AiOps-actions` | mock NOC ops (unchanged) |

OpenAPI schemas: `s3://reem-amdocs-ai-artifacts-3331/agent/iiq-*/openapi_schema.yaml`

## Path A — AgentCore Gateway (when available)

Run probe:

```powershell
python scripts/setup_agentcore_gateway.py --report-only
```

Output: `docs/MCP_PATH.json` with API availability and rationale.

Manual steps (console / preview API):

1. Create Cognito user pool + resource server + app client (OAuth2 client credentials or auth code).
2. Create AgentCore Gateway with inbound JWT authorizer (Cognito).
3. Register each enrichment Lambda as a gateway target with input schema from OpenAPI.
4. Note MCP endpoint URL and tool list in `.env` (`AGENTCORE_GATEWAY_URL`, etc.).

## Why Path B landed for the agent

- `invoke_agent` action groups are stable, documented, and already integrated in Flask trace parsing.
- AgentCore Gateway APIs vary by account/boto3 version; automating create without console access risks blocking the deadline.
- Teacher demo value: KB citations + three enrichment tools + session memory — all via action groups.

## Path C — Cursor IDE (developer MCP)

Use this when **you** (not the Bedrock agent) want Cursor to inspect AWS, query the KB, or capture screenshots.

**Prerequisites:** `uv` on PATH · AWS CLI profile `reemmor` in `~/.aws/credentials` · open workspace root `amdocs-ai-course` (not only `piter-aiops` subfolder).

Install (once per machine):

```powershell
# From repo root — .cursor/ is gitignored; copy the committed template
copy projects\piter-aiops\config\mcp.json.example .cursor\mcp.json
```

Then reload Cursor (**Settings → MCP** or window reload).

| Server | Package / URL | Use for PITER AiOps |
|--------|---------------|---------------------|
| `aws-api` | `uvx awslabs.aws-api-mcp-server@latest` | Bedrock agent `HH4YGSLZUE`, Lambdas, S3 `reem-amdocs-ai-artifacts-3331`, EC2 demo |
| `bedrock-kb` | `uvx awslabs.bedrock-kb-retrieval-mcp-server@latest` | Direct KB `RBTJM6NIG9` retrieval with citations |
| `aws-knowledge` | `https://knowledge-mcp.global.api.aws` | Live AWS / Bedrock documentation (no credentials) |
| `playwright` | `npx @playwright/mcp` | `scripts/capture_*.mjs` screenshot workflows |
| `course-tools` | Lecture 08 stdio server | Course demo tools (`get_weather`, `get_joke`) — requires `lectures/08_mcp/.venv` |

**Credential layout:** keys stay in `~/.aws/credentials`; MCP env uses `AWS_PROFILE=reemmor` and `AWS_REGION=us-east-1` only — same as [`docs/aws_credentials.md`](aws_credentials.md). Do **not** put access keys in `mcp.json`.

**Avoid:** `@aws/mcp-server-aws-api` (npm 404) and `mcp-server-aws-lambda` (not on PyPI). Use `awslabs.*` packages via `uvx`.

**Windows:** If `aws-api` / `bedrock-kb` stay red in Settings → MCP, set `command` to the full `uvx.exe` path from `where.exe uvx` (Cursor may not inherit shell PATH).

Verify:

```powershell
aws sts get-caller-identity --profile reemmor
```

In Cursor chat, confirm `call_aws` and KB retrieval tools appear under MCP.
