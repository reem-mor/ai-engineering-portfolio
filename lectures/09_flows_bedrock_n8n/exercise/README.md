# Exercise — Parse Bedrock Flow output in n8n

**Goal:** Extend `workflow_02_n8n_to_bedrock.json` so the webhook returns a clean `{ "summary": "..." }` instead of raw stream data.

---

## Background

`invoke_flow` returns a **stream of events**, not a single JSON object. A successful run ends with:

- `flowCompletionEvent.completionReason` = `"SUCCESS"`
- `flowOutputEvent.content.document` = the summary string

`invoke_flow.py` already collects these events in Python. Your job is to do the equivalent in n8n.

---

## Tasks

### 1. Confirm the Python baseline

```powershell
cd lectures\09_flows_bedrock_n8n
.\.venv\Scripts\Activate.ps1
python bedrock_flows\invoke_flow.py "Test paragraph for the exercise."
```

Note the summary output.

### 2. Import and run workflow 02

Follow [`n8n/README.md`](../n8n/README.md). Set n8n variables:

- `BEDROCK_FLOW_ID`
- `BEDROCK_FLOW_ALIAS_ID`
- `AWS_REGION`

Call the webhook and inspect the raw response.

### 3. Add a Code node (recommended approach)

Between **Invoke Bedrock Flow** and **Respond to Webhook**, insert a **Code** node:

1. Parse the HTTP response body (may be newline-delimited JSON events or a single blob).
2. Find the event containing `flowOutputEvent`.
3. Extract `content.document` as `summary`.
4. On failure, return `{ "error": "<reason>" }` with `completionReason` from `flowCompletionEvent`.

Starter logic (adapt to your actual response shape):

```javascript
const raw = $input.first().json.data ?? $input.first().json.body ?? '';
const lines = String(raw).split('\n').filter(Boolean);
let summary = null;
let error = null;

for (const line of lines) {
  try {
    const event = JSON.parse(line);
    if (event.flowOutputEvent?.content?.document) {
      summary = event.flowOutputEvent.content.document;
    }
    if (event.flowCompletionEvent?.completionReason &&
        event.flowCompletionEvent.completionReason !== 'SUCCESS') {
      error = event.flowCompletionEvent.completionReason;
    }
  } catch {
    // non-JSON line — skip
  }
}

return [{ json: summary ? { summary } : { error: error ?? 'No flowOutputEvent found' } }];
```

### 4. Update Respond to Webhook

Set response body to `={{ $json }}`.

### 5. Export your workflow

**Download** the updated workflow JSON and save as `n8n/workflow_02_exercise_solution.json` (optional — for your own reference; do not commit AWS credential IDs).

---

## Acceptance criteria

| # | Criterion |
|---|-----------|
| 1 | POST to `/webhook/bedrock-flow` with `{ "text": "..." }` returns HTTP 200 |
| 2 | Response JSON has `summary` key with a non-empty string on success |
| 3 | On invalid/missing flow IDs, response includes a clear `error` field |
| 4 | No AWS access keys hardcoded in the workflow JSON |

---

## Stretch goals

1. **Error handling:** Add an IF node — route failures to a Slack/email notification (mock with a second webhook).
2. **Dual path:** Use workflow 01 for quick model calls and workflow 02 when you need the governed Bedrock Flow version.
3. **Observability:** Log `executionId` from `flowCompletionEvent` to n8n execution data for traceability.

---

## Submission

Document in your homework folder (or PR description):

1. Screenshot of successful n8n execution.
2. Sample `curl` command and response body.
3. One paragraph: when would you use Bedrock Flows vs calling the model directly from n8n?
