# PITER AWS Phase 4 — Bedrock Agent Verification

**Audit date:** 2026-06-08  
**Agent ID:** `HH4YGSLZUE`  
**Alias ID:** `O2EM03R4R3` (`live`)

## Agent summary

| Field | Value |
|-------|-------|
| Name | `incidentiq-triage-agent` (legacy console name) |
| Status | **PREPARED** |
| Prepared at | 2026-06-08T09:27:48Z |
| Foundation model | Claude Haiku 4.5 inference profile (`us.anthropic.claude-haiku-4-5-20251001-v1:0`) |
| Agent role | `arn:aws:iam::329***579:role/incidentiq-agent-role` |
| Idle session TTL | 600s |
| Orchestration | DEFAULT; orchestration prompt **ENABLED** |
| Memory summarization prompt | **DISABLED** |
| Guardrail on agent | **null** (not attached at agent level) |

## Alias summary

| Field | Value |
|-------|-------|
| Alias name | `live` |
| Alias status | **PREPARED** |
| Invocation state | **ACCEPT_INVOCATIONS** |
| Routes to version | **3** (current since 2026-06-05) |

## Knowledge Base association (agent v3)

| KB ID | State | Description |
|-------|-------|-------------|
| `RBTJM6NIG9` | **ENABLED** | NOC/SRE runbooks, playbooks, escalation paths |

## Action groups (agent v3)

| Action group | State | Lambda | Maps to PITER final tool |
|--------------|-------|--------|--------------------------|
| `iiq-correlate` | ENABLED | `iiq-correlate` | **piter-recent-deployments** (legacy name) |
| `iiq-context` | ENABLED | `iiq-context` | **piter-service-context** (legacy name) |
| `iiq-similar` | ENABLED | `iiq-similar` | **piter-similar-incidents** (legacy name) |
| `incidentiq-ops` | ENABLED | `incidentiq-actions` | **Legacy** — env status/alerts/create incident |
| `incidentiq-ops-test` | DISABLED | — | Stale test group; safe to delete later |

**Not on agent:** `piter-escalation` (local only; not deployed to AWS).

## PITER instruction format compliance

Agent instruction (1628 chars, synced with `app/bedrock_agent_client.py` `AGENT_INSTRUCTION`) includes:

| Requirement | Present |
|-------------|---------|
| 1. Priority | Yes |
| 2. Investigation | Yes |
| 3. Triage | Yes |
| 4. Escalation | Yes |
| 5. Resolution | Yes |
| Prefer KB evidence and tool results | Yes |
| Do not invent owners/deployments/contacts/incidents | Yes |
| Ask for missing information | Yes ("Not in knowledge base") |
| Require confirmation before side effects | Yes (human sign-off, no auto-exec) |
| Cite sources | Yes |
| Confidence and uncertainty section | Yes |

**Verdict:** Instruction is **strong** and aligned with PITER workflow.

## Prompt quality gaps (recommendations only — do not mutate AWS)

1. **Attach Bedrock Guardrail** `rti921amc6u3` (DRAFT) to agent for credential-exfiltration and destructive-action topic blocks at the model layer.
2. **Enable memory summarization** if multi-turn sessions exceed idle TTL frequently.
3. **Rename** agent/action groups from `iiq-*` / `incidentiq-*` to `piter-*` for demo clarity (requires prepare-agent + alias update).
4. **Disable or remove** `incidentiq-ops` after confirming Flask/MCP no longer depend on `getEnvironmentStatus` / `createIncident` via agent path.
5. **Deploy `piter-escalation`** Lambda + action group so agent can preview/send escalations with confirmation token (currently app-side only).

## Commands run (read-only)

```powershell
aws bedrock-agent get-agent --agent-id HH4YGSLZUE
aws bedrock-agent get-agent-alias --agent-id HH4YGSLZUE --agent-alias-id O2EM03R4R3
aws bedrock-agent list-agent-knowledge-bases --agent-id HH4YGSLZUE --agent-version 3
aws bedrock-agent list-agent-action-groups --agent-id HH4YGSLZUE --agent-version 3
```
