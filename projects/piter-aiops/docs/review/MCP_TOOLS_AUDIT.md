# PITER AiOps — MCP / Tools Audit

Read-only audit · 2026-06-06

## What exists in this repository

| Capability | Present? | Evidence |
|------------|----------|----------|
| Real MCP server (stdio/HTTP MCP protocol) | **No** in app repo | No `@modelcontextprotocol` server implementation |
| MCP client in Flask app | **No** | |
| Bedrock action groups + Lambda | **Yes** | `action_groups/iiq-*`, setup scripts |
| MCP-style tool abstraction | **Yes** | `app/services/tool_router.py` — JSON `{"tool","arguments"}` contract |
| AgentCore Gateway probe | **Documented** | `scripts/setup_agentcore_gateway.py --report-only` |
| Course demo MCP server | **External** | Workspace MCP `course-tools` (weather/joke) — not part of piter-aiops runtime |

## Accurate wording for submission

> Bedrock action groups backed by AWS Lambda demonstrate the agent-tool workflow. The Flask app also exposes a deterministic tool registry (`tool_router.py`) that mirrors the same four enrichment operations for reliable demo triage. A separate AgentCore Gateway MCP path is documented for future external clients. This is **not** a standalone MCP server inside the Flask process.

## Tool registry (app layer)

| Tool name | Handler | Lambda equivalent |
|-----------|---------|-------------------|
| `correlate_deployments` | `enrichment_tools.correlate_deployments` | `iiq-correlate` |
| `lookup_owner_and_escalation` | `enrichment_tools.lookup_owner_and_escalation` | `iiq-context` `/owner` |
| `score_business_impact` | `enrichment_tools.score_business_impact` | `iiq-context` `/impact` |
| `find_similar_incidents` | `enrichment_tools.find_similar_incidents` | `iiq-similar` |

## Documentation accuracy

| Doc | MCP claim | Accurate? |
|-----|-----------|-----------|
| `docs/MCP_PATH.md` | Distinguishes action groups vs AgentCore | **Yes** |
| `README.md` | References MCP/tools concept | **OK** if clarified as action groups + tool router |
| `evaluation/live_smoke_summary.md` | Says "4-tool MCP enrichment" | **Acceptable** as conceptual; prefer "tool router" in grading email |

## Optional Path A (AgentCore Gateway)

- Script: `scripts/setup_agentcore_gateway.py`
- Status: probe/report only unless account supports Gateway API
- Does not block submission

## Recommendation

For teacher video: demonstrate **tool use** via (1) triage card tool sections populated, (2) optional terminal run of `agent_smoke_test.py --ops` showing agent calling ops action group, (3) cite `docs/MCP_PATH.md` for terminology honesty.
