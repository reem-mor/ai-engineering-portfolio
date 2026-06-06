# MCP integration path (Phase 3)

## Decision

| Path | Status | Role |
|------|--------|------|
| **B — Bedrock action groups** | **Deployed** | Reliable tool path for `invoke_agent` (iiq-correlate, iiq-context, iiq-similar) |
| **A — AgentCore Gateway (MCP)** | **Documented / probe** | Same Lambdas exposed as MCP tools with Cognito OAuth when account supports it |

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
