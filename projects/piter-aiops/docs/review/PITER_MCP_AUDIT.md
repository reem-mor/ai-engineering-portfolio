# PITER AiOps — MCP / Tools Audit

- **Author:** Re'em Mor
- **Date:** 2026-06-07

## Accurate terminology
- **Production tool path:** Bedrock **Action Groups** backed by AWS **Lambda** (the 4 PITER tools).
  This is *not* MCP and is not described as such.
- **MCP story:** a standardized **local/demo tool-contract layer** mapping to the same 4 PITER tools.

## Current state (before this pass)
| Classification | Present? | Evidence |
| -------------- | -------- | -------- |
| Real MCP server | No | no `mcp/server.py` |
| MCP-style tool contracts | Partial | `app/services/tool_router.py`, `docs/mcp.md`, `docs/MCP_PATH.md/.json` |
| Bedrock action groups | Yes | `action_groups/piter-*` |
| IDE MCP client config | Yes | `config/mcp.json.example` (aws-api, bedrock-kb, playwright …) |

## Change in this pass (Commit 5 — additive, read-only)
Add a minimal, **read-only** MCP scaffold mapping the same four PITER tools, reading from
`data/source` (no duplicate datasets, no AWS/network calls):

```
mcp/
├── README.md          # what this is / how it maps to action groups
├── server.py          # stdio MCP server exposing 4 read-only tools
├── tools/             # tool implementations delegating to app.enrichment_tools
├── schemas/           # JSON Schemas for each tool's input/output
└── examples/          # sample requests/responses
```

Constraints honored:
- Read-only by default; no network/AWS calls.
- Reuses `app/enrichment_tools.py` (single source of truth) — no dataset duplication.
- escalation exposed only in **preview/mock** form (no sending).

## Honest claims
- We do **not** claim Bedrock Action Groups are MCP.
- We do **not** claim auto-sync between MCP and AWS.
- MCP here demonstrates the *tool-contract* concept the course asks for, in a runnable local form.

## Status: PARTIAL → addressed by additive `mcp/` scaffold; production tools remain Action Groups.
