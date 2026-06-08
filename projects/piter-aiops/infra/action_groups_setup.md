# Action Groups Setup

Create one action group per tool:

- `piter-recent-deployments`
- `piter-service-context`
- `piter-similar-incidents`
- `piter-escalation-preview`

Each action group should expose a small OpenAPI schema and invoke a Lambda that returns JSON-compatible output.

Local source mapping:

- `mcp/recent_deployments.py`
- `mcp/service_context.py`
- `mcp/similar_incidents.py`
- `mcp/escalation.py`
