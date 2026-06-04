# InvokeAgent API verification (Firecrawl vs `bedrock_agent_client.py`)

**Date:** 2026-06-03  
**Sources (live, scraped via Firecrawl):**

- [InvokeAgent API](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_InvokeAgent.html) → `.firecrawl/bedrock-invokeagent.md`
- [Trace events](https://docs.aws.amazon.com/bedrock/latest/userguide/trace-events.html) → `.firecrawl/bedrock-trace-events.md`
- [Observation](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_Observation.html) → `.firecrawl/bedrock-observation.md`
- [ActionGroupInvocationOutput](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_ActionGroupInvocationOutput.html) → `.firecrawl/bedrock-action-group-output.md`
- [TracePart](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent-runtime_TracePart.html) → `.firecrawl/bedrock-trace-part.md`

**Code:** [`app/bedrock_agent_client.py`](../app/bedrock_agent_client.py)

## Summary

The client’s hand-built `invoke_agent` request and stream parsing **align with the current AWS contract** for the fields it uses. No blocking mismatches. Several **optional request/response capabilities** exist in the API but are intentionally unused; a few **citation/enrichment gaps** are worth follow-up if you expand KB sources or multi-agent setups.

## Request fields (`ask()`)

| Field | Code | Live docs | Status |
|-------|------|-----------|--------|
| `agentId` | Yes | Path + body | OK |
| `agentAliasId` | Yes | Path + body | OK |
| `inputText` | Yes | Documented; ignored if `returnControlInvocationResults` in `sessionState` | OK (not using return-control) |
| `sessionId` | Yes | Reuse for same conversation | OK |
| `enableTrace` | `True` | Trace enablement | OK |
| `sessionState.sessionAttributes` | Yes | `SessionState` | OK |
| `sessionState.promptSessionAttributes` | Yes | `SessionState` | OK |

**Not used (documented, optional):** `endSession`, `memoryId`, `bedrockModelConfigurations`, `promptCreationConfigurations`, `streamingConfigurations`, `sessionState.conversationHistory`, `sessionState.files`, `sessionState.returnControlInvocationResults`, `sessionState.knowledgeBaseConfigurations`, etc. No drift—just scope.

## Streaming response (`completion` events)

| Path | Code | Live docs | Status |
|------|------|-----------|--------|
| `chunk.bytes` | Decode UTF-8, join | Final answer in `bytes` | OK |
| `chunk.attribution.citations[].retrievedReferences` | Collected | Same structure in response syntax | OK |
| `trace` → `trace` (TracePart) → `orchestrationTrace` | `inner = trace.get("trace") or trace` | TracePart wraps union `trace`; orchestration step documented | OK |
| `orchestrationTrace.observation.knowledgeBaseLookupOutput.retrievedReferences` | Merged into citations | Observation + trace-events | OK |
| `orchestrationTrace.observation.actionGroupInvocationOutput` | `_merge_action_output` | Observation API; `text` is JSON string | OK |
| `response.sessionId` | `out_session_id` | Response header / stream metadata | OK |

**Not handled (documented):**

- Stream **errors** surfaced in response (`accessDeniedException`, `throttlingException`, etc.)—boto3 may raise; code relies on `translate(exc)` on client errors only.
- **`returnControl`** payload for RETURN_CONTROL action groups.
- **`files`** (code interpreter artifacts).
- **Other trace steps:** `preProcessingTrace`, `postProcessingTrace`, `customOrchestrationTrace`, `guardrailTrace`, collaborator routing traces—only orchestration observations are mined.
- **Multi-chunk streaming:** Docs note one chunk for the full interaction today; code already concatenates all `bytes` (future-safe).

## Reference parsing (`_parse_references`)

| Field | Code | Live docs | Status |
|-------|------|-----------|--------|
| `content.text` | Required for snippet | Documented | OK |
| `location.s3Location.uri` | Primary label source | One of many `location` types | **Partial** |
| `metadata` (score, chunk id) | `extract_reference_metadata` | `metadata` map on references | OK |

**Gap:** References can use `confluenceLocation`, `webLocation`, `kendraDocumentLocation`, `sharePointLocation`, etc. Code only reads `s3Location.uri`; non-S3 KB sources would show as “Unknown source” unless extended.

## Action group enrichment (`_merge_action_output`)

| Behavior | Code | Live docs | Status |
|----------|------|-----------|--------|
| Read JSON from `actionGroupInvocationOutput.text` | Yes | `ActionGroupInvocationOutput.text` | OK |
| Keys: `deployments`, `owner_team`, `similar_incidents`, … | App-specific | N/A (Lambda contract) | OK |

## Recommended follow-ups (non-blocking)

1. **Citation locations:** Map `location.type` / non-S3 URIs when KB data sources are not S3-only.
2. **Session lifecycle:** Expose `endSession` when closing a triage session if you need explicit session teardown.
3. **Return control:** If any action group uses RETURN_CONTROL, parse `returnControl` and pass `returnControlInvocationResults` in `sessionState` per docs.
4. **Trace coverage:** Optionally log `preProcessingTrace` / `postProcessingTrace` for debugging guardrails or reprompts.
5. **Re-verify after AWS changes:** Re-run Firecrawl scrape on InvokeAgent + trace-events when upgrading Bedrock Agent Runtime SDK or agent versions.

## Why Firecrawl helped here

Built-in fetch often returns cookie banners or truncated HTML on AWS docs. Firecrawl produced **main-content markdown** suitable for grep-driven verification, discovered related API pages via `map --search InvokeAgent`, and cached artifacts under `.firecrawl/` for repeatable audits without stuffing the context window.
