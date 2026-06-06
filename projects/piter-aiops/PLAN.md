# PLAN — PITER AiOps: Answer UI Redesign + AWS/Docker + Screenshots

Scope: only `projects/incident-rag-bedrock/`. Do not change overall theme/nav/layout.

## PART A — Answer output section (fully in my control)
Targets: `frontend/src/components/FormattedAnswer.tsx` (+ new `CodeBlock.tsx`,
`lib/answer-format.ts`), and minimal call-site edits in `frontend/src/App.tsx`.

- A1 Code blocks: parse SQL/shell/python out of step text + citation snippets;
  render as `<pre>` blocks (mono, distinct bg, rounded border, padding, preserved
  whitespace). Syntax highlighting via a small dependency-free tokenizer
  (lighter than highlight.js/Prism — no install, no bundle bloat). Copy button +
  language badge per block. Group a step's multiple statements as a session with
  "Copy all". Destructive SQL (`pg_terminate_backend`, `DROP`, `DELETE FROM`,
  `TRUNCATE`, `kill -9`, `rm -rf`) gets an amber left-border + "destructive" label.
  SQL text itself is never modified.
- A2 Command emphasis: steps whose core action is a command get a run icon +
  bold action; prose-only steps stay normal weight.
- A3 Interactivity: Recommended steps become a client-side checklist; sections
  get headers/dividers/spacing; Retrieved citations become collapsible (collapsed
  by default). Body text bumped to `foreground/90` for WCAG AA contrast.
- A4 Corpus block: move `<DocumentUpload />` to sit with the Knowledge Base flow
  (after Live KB), relabel eyebrow "Knowledge Base — manage corpus". Keeps the
  triage view focused. Low-risk reorder; `#document-upload` id preserved.
- Verify: build + Playwright MCP at 390 / 768 / 1440 (copy, checklist, collapse).

Decision log:
- Highlighter: custom regex tokenizer (SQL + bash), not highlight.js/Prism.
  Reason: lightest option, no network install, no added dependency/bundle weight.

## PART B — AWS + Docker (needs cost confirmation before paid resources)
AWS identity OK: account `329597159579`, user `admin-reem`. Region not set in
profile — will pass `--region` explicitly (app default region TBD from `.env`).

- B1 S3: confirm/create `reem-amdocs-ai-artifacts-3331` + prefix; upload corpus; tag.
- B2 Bedrock KB: confirm/create KB + data source; **PAUSE for cost** before
  OpenSearch Serverless (~$0.24/hr ≈ ~$175/mo if left on). Sync; report IDs.
- B3 Docker: build from project Dockerfile; run locally; capture `docker ps`.
- B4 EC2: launch tagged t3.micro; install Docker; run; least-privilege SG;
  IAM role for Bedrock. **PAUSE for cost** before launch (~$0.0104/hr t3.micro).

## PART C — Screenshots → `screenshots/`
Local (I can do): Flask app, Q&A example, docker ps, pytest, redesigned home.
Console (need your login): Bedrock KB, sync status, EC2 details, public app.

## TEARDOWN
List every created resource; on go-ahead delete paid ones (EC2, OpenSearch);
keep S3 unless told otherwise; cleanup note in README.

## Gates requiring user input
1. Cost confirmation for OpenSearch Serverless (B2) and EC2 (B4).
2. AWS console login/MFA for console screenshots (C).
