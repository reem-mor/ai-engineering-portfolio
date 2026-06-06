# PITER AiOps: AI-Powered Incident Operations for Faster Resolution

6-slide presentation outline (5–7 minute live demo).

A 5–7 minute live-demo deck. One slide per section, in the required order.

---

## Slide 1 — About Me

- Re'em Mor — NOC / SRE engineer, background in high-availability operations.
- Day job: triaging production alerts under time pressure.
- Why this project: turn the 5–15 minutes lost per incident hunting for the
  right runbook into seconds of grounded, cited guidance.

---

## Slide 2 — Project Overview

- **PITER AiOps**: five golden pillars — **Priority, Investigation, Triage, Escalation, Resolution**.
- Tagline: *From Alert to Resolution, Faster.*
- Input: a production alert (service, environment, severity, symptom).
- Output: **one PITER triage card** — priority class, investigation findings, triage plan,
  escalation recommendation, resolution plan, business impact, sources, confidence.
- Two backends, same UX: **local offline mode** (default, reliable demo) and an
  optional **Amazon Bedrock Agent + Knowledge Base** mode.
- Demo scenario: *Postgres CPU 95% on `prod-db-1`, NJ-DGE, P2.*

---

## Slide 3 — Technologies Used

- **Python 3.12**, **Flask 3** (JSON API + HTML console), **gunicorn**.
- **RAG**: local pure-Python TF-IDF retriever over `knowledge_base/runbooks/`;
  Bedrock Knowledge Base when enabled.
- **MCP / tools**: a JSON tool-router driving **4 enrichment tools**.
- **Data**: Pandas + CSV + JSON (`data/` deploys, catalog, impact matrix,
  incident history, external status).
- **Docker** (multi-stage, non-root, healthcheck); optional **EC2** + **boto3**.
- **pytest** — 189 offline tests, zero live AWS calls.

---

## Slide 4 — System Architecture

```
User → Flask Web App → Agent (local or Bedrock)
            ├─ RAG Knowledge Base (runbooks, cited)
            ├─ MCP / Tools (4 enrichment tools)
            └─ Session Memory (follow-ups)
                      ↓
              One Triage Card (JSON)
```

- `POST /api/triage` → retrieve runbook + run 4 tools + compose card.
- `POST /api/follow-up` → reuse session memory (no re-run of tools).
- Bedrock failure auto-falls back to local mode → the demo never fails.

---

## Slide 5 — Live Demo

1. Open `http://localhost:8080/console` → **Load demo alert**.
2. **Run triage** → show the cited RB-007 answer + numbered steps.
3. Point out: suspect deploy, owner/escalation, business impact, similar incidents.
4. Follow-up: *"who do I escalate to?"* → answered **from memory** (no re-run).
5. Off-topic question → **"Not in knowledge base"** refusal (no hallucination).

Backup if anything is slow: `pytest -q` (189 passing) and `docker compose up`.

---

## Slide 6 — Challenges & Next Steps

- **Challenges**: making the demo robust without AWS (local TF-IDF RAG +
  deterministic tools + auto-fallback); keeping tool outputs structured and
  crash-proof; tuning the retrieval threshold so off-topic queries refuse.
- **Next steps**: embeddings-based local retrieval, persist session memory in
  Redis/SQLite for multi-instance, deploy the 4 tools as real Lambda/MCP
  endpoints, and add an evaluation harness for answer quality.
