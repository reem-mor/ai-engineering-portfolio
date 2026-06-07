# PITER AiOps — MCP tool layer (read-only)

This folder is the **MCP (Model Context Protocol) tool-contract layer** for PITER AiOps. It exposes
the same four PITER tools as the production **Bedrock Action Groups**, but as a local, runnable MCP
server so the tool contracts can be inspected and demonstrated without AWS.

## Accurate terminology
- **Production tool path:** Bedrock **Action Groups** backed by AWS **Lambda** (`action_groups/piter-*`).
  This is *not* MCP.
- **This layer:** a standardized **MCP** server mapping 1:1 to the same four tools, for local
  demo / contract review / future portability.

> We do **not** claim Bedrock Action Groups are MCP, and there is **no** auto-sync between the two.
> Both simply delegate to the same business logic in `app/enrichment_tools.py` (single source of truth).

## The four tools (read-only)
| MCP tool | Maps to Lambda | Backing function |
| -------- | -------------- | ---------------- |
| `recent_deployments` | `piter-recent-deployments` | `correlate_deployments` |
| `service_context` | `piter-service-context` | `lookup_owner_and_escalation` + `score_business_impact` |
| `similar_incidents` | `piter-similar-incidents` | `find_similar_incidents` |
| `escalation_preview` | `piter-escalation` (preview only) | `lookup_owner_and_escalation` (masked, **never sends**) |

## Safety
- **Read-only:** no AWS calls, no network, no notifications.
- `escalation_preview` returns a **masked** recipient and `sends_notifications: false`. Live dispatch
  is only reachable through the gated Flask/Lambda path, never from MCP.
- No duplicate datasets — tools reuse `app.enrichment_tools`, which reads the canonical
  `data/` sources.

## Run
```bash
cd projects/piter-aiops
python -m mcp.server            # stdio MCP server (newline-delimited JSON-RPC)
python mcp/server.py --selftest # offline self-test, no MCP client needed
```

Quick manual stdio check:
```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | python mcp/server.py
```

## Use from an MCP client (example config)
```json
{
  "mcpServers": {
    "piter-aiops": {
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "projects/piter-aiops"
    }
  }
}
```

## Layout
```
mcp/
├── README.md       # this file
├── server.py       # stdlib-only MCP stdio server (initialize, tools/list, tools/call)
├── tools/          # tool implementations delegating to app.enrichment_tools
├── schemas/        # JSON Schema per tool (generated from the server definitions)
└── examples/       # sample tool-call requests + response key summaries
```

## Protocol
Implements the JSON-RPC 2.0 subset of MCP (`protocolVersion 2024-11-05`): `initialize`,
`notifications/initialized`, `tools/list`, `tools/call`. Stdlib only — independent of the official
`mcp` PyPI SDK (so it runs with no extra dependencies).
