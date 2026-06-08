# PITER MCP / Tools Audit

## Accurate architecture statement

| Layer | Technology | Status |
|-------|------------|--------|
| **Production tools** | Bedrock Action Groups → AWS Lambda | Deployed (3× iiq + ops) |
| **MCP** | Local `mcp/server.py` stdio JSON-RPC | Implemented read-only |
| **App tools** | `app/enrichment_tools.py` + `tool_router.py` | Used by Flask triage |

**We do NOT claim** Bedrock Action Groups are MCP.

## MCP folder structure

```
mcp/
├── README.md       ✓
├── server.py       ✓
├── __init__.py
└── tools/
    └── piter_tools.py
```

Missing vs user proposal: `schemas/`, `examples/` subdirs — optional nice-to-have.

## Tool mapping

| MCP tool | Bedrock / app function |
|----------|---------------------|
| `recent_deployments` | `correlate_deployments` |
| `service_context` | owner + impact |
| `similar_incidents` | `find_similar_incidents` |
| `escalation_preview` | masked preview only |

## Safety

- MCP server: no network, no AWS, no sends (`mcp/README.md`)
- Matches course story for "tools concept"

## Gap

- MCP not wired into Flask production path — demonstration / contract review only
- AgentCore gateway script exists (`scripts/setup_agentcore_gateway.py`) — optional future path
