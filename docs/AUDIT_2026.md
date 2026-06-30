# Portfolio Audit 2026 — `amdocs-ai-course`

> **Historical audit (2026-06-27).** Many items below are **resolved** — CI, AGENTS.md, resources manifest-only, README reframed, flagships in [`flagships/`](../flagships/). See [`README.md`](../README.md) and [`docs/SYLLABUS.md`](SYLLABUS.md) for current state.

> **Read-only audit.** This document changes nothing in the repo. It is the approval
> artifact for the cleanup work that follows (Prompts 2–4 of the overhaul plan).
> Author context: **Re'em Mor — "AI Engineer × SRE"**, targeting 2026 AI-engineering roles.
> Date: 2026-06-27.

---

## Executive summary — top 5 things to fix for employer-readiness

1. **The README features the wrong flagship and is two milestones stale.** It leads with
   *IncidentIQ (incident-assistant-rag)* as "the main portfolio project" and lists only
   **1 of the repo's 4 projects**. PITER AiOps — the most advanced, agentic, best-tested
   project (17.3k LOC, 301 tests, live EC2) — is buried under `projects/`, and the
   `oz_veruach_bot` standalone product isn't mentioned at all. Milestones stop at lecture 08
   but lecture 09 exists. **Reframe the repo as a course/learning archive that links OUT to
   flagship repos.**
2. **Repo is heavy with third-party IP.** `resources/` is **20 MB of Amdocs lecture PDFs and
   assignment handouts** (6 PDFs + 5 DOCX/PPTX) — instructor-copyrighted material that
   should not be redistributed in a public repo. The `.git` directory is **59 MB** (over
   half the 112 MB repo), largely these binaries. Remove from the tree and purge from history.
3. **Agent/tooling config is duplicated and rudderless.** There is **no `CLAUDE.md` and no
   `AGENTS.md`** (both absent — the plan assumed `CLAUDE.md` exists; it does not). Meanwhile
   the skill tree is **mirrored across `.cursor/skills/` and `.agents/skills/`** (29 files
   each; 24 byte-identical, 5 differ only by a buggy "Claude"→"Codex" string swap). Plus 89
   committed `.playwright-mcp/*.yml` snapshot junk and several dead MCP servers.
4. **Broken/inconsistent tooling.** Root `requirements.txt` is **UTF-16 LE** (breaks
   `pip install -r` and plain `cat`/grep). Python 3.12 is documented but pinned in only one
   of nine dependency files. **No CI anywhere** in the repo despite the README promising it.
5. **Good news, stated plainly: no committed secrets.** A full working-tree + git-history
   scan found **zero real keys/tokens** (the README's "early experiments may contain
   hardcoded tokens" caveat is unfounded — drop it). The one real exposure is **live AWS
   resource identifiers** (KB IDs, agent IDs, EC2 instance IDs/hostnames) hardcoded in the
   PITER docs/config — scrub/parameterize these before extracting PITER to a public repo.

---

## KEEP / FIX / MERGE / REMOVE / MOVE table

### 1. Repository identity

| Item | Verdict | Rationale |
|------|---------|-----------|
| Repo name `amdocs-ai-course` | **KEEP (decide once)** | Recognizable as coursework; GitHub auto-redirects if later renamed to e.g. `ai-engineering-coursework`. Low value to rename — the bigger lever is reframing the README, not the slug. |
| Repo description / topics | **FIX (manual)** | Add description + topics (`ai-engineering`, `rag`, `aws-bedrock`, `llm`, `sre`, `python`, `docker`). Manual GitHub step. |
| README framing | **FIX** | Currently frames repo as a single-flagship portfolio. Re-frame as **course + learning archive** that links OUT to flagship repos (PITER AiOps, HINDSIGHT). Lead with "AI Engineer × SRE". |

### 2. Top-level clutter

| Item | Verdict | Rationale |
|------|---------|-----------|
| `current-home.png` (241K) | **MOVE → `docs/assets/`** | Stray PITER session working file at root; only referenced (by bare, broken path) from a PITER doc. Move with PITER or into `docs/assets/`. |
| `reference-chat.png`, `reference-home.png`, `reference-storm.png` (321K) | **MOVE → `projects/piter-aiops/screenshots/`** | PITER reference shots dumped at root; fix the broken prose references in `PITER_OPS_ENTERPRISE_REPORT.md`. |
| `phase0-dashboard-top.png` (97K) | **REMOVE** | Orphaned — referenced nowhere. |
| `assets/profile-banner.png` (512K) | **REMOVE** (or wire into README) | Orphaned — not embedded in any markdown. Remove, or intentionally add to README header. |
| `.playwright-mcp/` (89 `.yml`) | **REMOVE + gitignore** | Generated a11y-snapshot junk (`page-<timestamp>.yml`) committed by accident. Untrack and add to `.gitignore`. |

### 3. Course material (IP)

| Item | Verdict | Rationale |
|------|---------|-----------|
| `resources/lecture0{1..6}*.pdf` (~19.5 MB) | **REMOVE (public) + purge history** | Amdocs instructor slides — third-party copyright. Keep originals in Drive; leave a manifest. Dominant contributor to the 59 MB `.git`. |
| `resources/handouts/*.docx`, `*.pptx` (~478K) | **REMOVE (public) + purge history** | Assignment briefs authored by the course — third-party copyright. Replace with a short text manifest. |
| `lectures/`, `homework/` write-ups, notebooks, demo code | **KEEP** | Author's own work; no embedded third-party binaries found. The learning archive's substance. |
| `lectures/09_flows_bedrock_n8n/` | **KEEP + surface in README** | Real content (Bedrock Flows + n8n, 10 workflows) the README omits. |

### 4. Projects

| Project | Verdict | Rationale |
|---------|---------|-----------|
| `projects/piter-aiops` | **MOVE-TO-OWN-REPO** | Intended flagship; confirmed most advanced — agentic (Bedrock Agent + 4 Action-Group Lambdas + MCP), session memory, alert-storm sim, escalation safety, **17.3k Py LOC, 301 tests**, live EC2, deck. Extraction-clean (only S3-prefix coupling). |
| `projects/incident-assistant-rag` (IncidentIQ) | **FEATURE (keep, link out)** | Genuinely distinct stack (FastAPI + OpenAI + **local FAISS**, no AWS); designated course capstone; 90 tests; doesn't overlap PITER's code. Feature it as the non-AWS RAG capstone. |
| `projects/incident-rag-bedrock` | **MERGE/RETIRE → label as learning iteration** | Confirmed code-ancestor of PITER (shares **12 byte-identical `app/` modules`**); PITER is a strict superset. Keep only as a clearly labeled "Bedrock RAG stepping-stone" or retire to avoid looking redundant. |
| `oz_veruach_bot/` (repo root) | **MOVE-TO-OWN-REPO (eventually)** | Unrelated, polished standalone product (course Telegram bot; async, **uv + mypy-strict + ruff + Alembic + 203 tests**, MIT). Zero monorepo coupling — a separate repo sitting in the wrong place. Out of scope for this pass; flag for a later extract. Per the cleanup constraints, **do not modify its internals**. |

### 5. Secrets & security

| Item | Verdict | Rationale |
|------|---------|-----------|
| Working tree secrets | **KEEP/clean** | No real keys found. `.env.example` files contain placeholders only; MCP config uses `${env:...}` interpolation and AWS named profiles. |
| Git-history secrets | **KEEP/clean** | No `.env`, `*.pem`, or `*.key` ever committed; no provider-key literal in any commit on any branch. |
| Live AWS identifiers in PITER | **FIX (before public extract)** | KB IDs, agent IDs, EC2 instance IDs/public hostnames hardcoded in PITER docs/config. Not secrets, but parameterize/scrub before PITER goes public. |
| README "hardcoded tokens" caveat | **REMOVE** | Unfounded by the scan; it reads worse than reality. Delete it. |

### 6. Dependencies & tooling

| Item | Verdict | Rationale |
|------|---------|-----------|
| Root `requirements.txt` (UTF-16) | **FIX** | Re-encode to UTF-8 (or split per-area and delete root if redundant). It's a `pip freeze` dump. |
| Python version pinning | **FIX** | 3.12 documented everywhere but pinned only in `oz_veruach_bot`. Add `.python-version` / pin in the kept Python areas. |
| `uv` vs `pip` | **KEEP (note)** | Only `oz_veruach_bot` uses uv; rest use pip. Acceptable; document per-area. |
| Cross-project version drift | **KEEP (note)** | Independent envs (Flask 3.0.3 vs 3.1.3, boto3 pins, faiss versions). Acceptable but worth noting. |

### 7. Agent / AI config

| Item | Verdict | Rationale |
|------|---------|-----------|
| `AGENTS.md` (missing) | **FIX → create canonical** | Make `AGENTS.md` the single cross-tool source of truth. |
| `CLAUDE.md` (missing) | **FIX → create, sourcing `@AGENTS.md`** | Thin file that includes `@AGENTS.md`. |
| `.cursor/skills/` vs `.agents/skills/` | **MERGE/de-dupe** | 29 files mirrored (24 identical, 5 differ only by a buggy Claude→Codex swap that produced artifacts like `.Codex/skills/...`). Keep one canonical tree; reference/remove the other. |
| `.cursor/rules/secrets-and-mcp-security.mdc` | **KEEP** | Good security rule; align with `AGENTS.md`. |
| `.cursor/settings.json` plugins (`firecrawl`, `deploy-on-aws`) | **FIX** | `firecrawl` has no usage evidence — drop. `deploy-on-aws` plausibly used — keep. |

### 8. MCP / integrations

| Server | Verdict | Rationale |
|--------|---------|-----------|
| n8n-workflows, aws-api, bedrock-kb, aws-knowledge, playwright, lovable | **KEEP** | Usage evidence in code/docs/`.env.example`. |
| `course-tools` | **FIX** | Real server (`lectures/08_mcp/server/tools_server.py`) but config points at a non-existent Windows `.venv` path. Fix path or drop. |
| context7, sequential-thinking, perplexity | **REMOVE (dead)** | Zero usage references; perplexity hits are an n8n node, not the MCP server. |
| `.cursor/mcp.json` → `.mcp.json` | **FIX** | No canonical `.mcp.json` exists. Produce a minimal project-scope `.mcp.json` with only the kept servers. |

### 9. Docs

| Item | Verdict | Rationale |
|------|---------|-----------|
| Root `README.md` | **FIX** | Strong format, but stale (omits lecture 09, projects 2–4, `oz_veruach_bot`) and mis-frames the flagship. No dead links found — issue is omission. |
| `docs/*` (course-summary, setup, etc.) | **KEEP** | Clean, accurate, no dead links. |
| `CONTRIBUTING.md` | **KEEP (note)** | Misnamed — it's a homework-submission procedure, not OSS contribution guidance. Acceptable for a course repo; optionally rename. |
| `LICENSE` (MIT, 2026 Re'em Mor + IP carve-out) | **KEEP** | Correct, with a sensible `resources/` carve-out. |
| `docs/submission-checklist.md` → `homework_submission_procedure.docx` | **FIX (minor)** | References a file not in repo (self-flagged). Drop the reference. |

### 10. CI / quality

| Item | Verdict | Rationale |
|------|---------|-----------|
| GitHub Actions | **FIX → add** | None exists anywhere. Add a minimal `ruff + pytest` workflow for the kept Python areas so the repo shows green checks. |
| pytest config | **KEEP** | Present in 5 places (per-project). |
| ruff/mypy config | **FIX** | Only `oz_veruach_bot` has lint config. Add a root `ruff` config covering kept areas. |

---

## Secrets & git-history risk (redacted) + remediation runbook

### Scan result

A full scan of the **working tree** and **complete git history** (`git log --all -p`,
all branches and remotes) for provider-key patterns (`sk-`, `sk-ant-`, `AKIA`, `ghp_`,
`hf_`, `AIza`, `xoxb-`/`xoxp-`), private-key blocks, AWS secret keys, and generic
`api_key`/`token`/`password`/`secret` assignments returned:

> **Zero real secrets.** No `.env`, `*.pem`, or `*.key` file was ever committed on any
> branch. Every pattern match resolved to one of: a placeholder (`your_..._here`), a
> documentation/tutorial example (`DB_PASSWORD="my****"`), an env-var reference
> (`${env:...}`), an AWS **named profile** (not raw keys), an SSM **parameter path name**
> (not a value), or a runtime secret accessor (`settings.smtp_pass.get_secret_value()`).

All findings below are **redacted** and are **not** live secrets:

| Type | File | Location | Redacted form | Real? |
|------|------|----------|---------------|-------|
| OpenAI / Gemini / HF / n8n / Lovable | `.env.example` (root) | HEAD + history | `*_KEY=your_…REDACTED…_here` | Placeholder |
| DB password / API token | `.agents|.cursor/skills/mcp-integration/references/authentication.md` | HEAD + history | `DB_PASSWORD="my****"`, `API_TOKEN="your-…-here"` | Placeholder (doc example) |
| MCP env refs | `.cursor/mcp.json` | HEAD + history | `N8N_API_KEY=${env:…}` | Not a secret (interpolation) |
| SSM param mapping | PITER infra (history) | history | `…_TOKEN = "/piter-aiops/notification/confirmation_token"` | Not a secret (path name) |
| SMTP password accessor | `oz_veruach_bot/app/services/email.py` | HEAD | `settings.smtp_pass.get_secret_value()` | Not a secret (runtime read) |

### The one real exposure (not a secret, but fix before going public)

PITER docs/config hardcode **live AWS resource identifiers**: Bedrock KB ID (`RBTJM6NIG9`),
agent ID (`HH4YGSLZUE`), EC2 instance ID (`i-0c53b195878f0ea5f`), and public EC2 hostnames.
These are not credentials, but they reveal infra topology and should be **parameterized via
env / `.env.example`** before PITER is extracted to a public repo.

### Remediation runbook

1. **Rotate:** Nothing strictly required — no live key is exposed. As hygiene, if any of the
   placeholder-named services were ever used with a real key locally, rotate out of caution.
2. **Scrub AWS identifiers** in PITER (do this during PITER standalone prep, Prompt 3-A):
   replace KB/agent/instance IDs and hostnames with `${ENV_VAR}` placeholders + `.env.example`.
3. **History purge — only needed for the large copyrighted binaries**, not secrets. Run
   deliberately, outside the cleanup PR (documented in `docs/SECURITY_REMEDIATION.md` by
   Prompt 2):
   ```bash
   # Remove Amdocs course binaries from ALL history (shrinks the 59 MB .git):
   pip install git-filter-repo
   git filter-repo --path resources/ --invert-paths \
                   --path-glob '*.pdf' --path-glob '*.pptx' --path-glob '*.docx' --invert-paths
   # Or BFG equivalent:
   #   bfg --delete-folders resources --delete-files '*.{pdf,pptx,docx}'
   # Then force-push (coordinate — rewrites history):
   git push --force-with-lease origin <branch>
   ```
4. **Confirm coverage:** `.gitignore` already covers `.env`, `*.pem`, `*.key`, FAISS,
   `*.sqlite`, `node_modules`, `.venv`, `.firecrawl`. **Add `.playwright-mcp/`** (currently
   tracked, 89 files). `.env.example` coverage is good.

> Reminder: never print real secret values in any PR, issue, or doc.

---

## Proposed target repository tree (cleaned `amdocs-ai-course`)

```text
amdocs-ai-course/                      # "Course + learning archive" — flagships link OUT
├── README.md                          # Reframed: AI Engineer × SRE + repo map + Featured work (links out)
├── AGENTS.md                          # Canonical cross-tool agent guidance (NEW)
├── CLAUDE.md                          # Thin: `@AGENTS.md` (NEW)
├── LICENSE                            # MIT + IP carve-out (kept)
├── CONTRIBUTING.md                    # Homework/submission workflow (kept)
├── .gitignore                         # + .playwright-mcp/
├── .env.example                       # placeholders only (kept)
├── .mcp.json                          # NEW — minimal, only used servers
├── requirements.txt                   # UTF-8 (re-encoded) — or split per-area
│
├── .github/workflows/ci.yml           # NEW — ruff + pytest, green checks
│
├── .cursor/                           # rules + settings + ONE canonical skills tree
│   ├── settings.json                  # firecrawl dropped; deploy-on-aws kept
│   ├── rules/secrets-and-mcp-security.mdc
│   └── skills/                        # single source of truth (de-duped)
│       └── → referenced by .agents/ (or .agents/ removed)
│
├── docs/
│   ├── AUDIT_2026.md                  # this report
│   ├── SECURITY_REMEDIATION.md        # NEW — history-purge runbook + rotate list
│   ├── course-summary.md  setup.md  submission-checklist.md  ...
│   ├── architecture/  diagrams/
│   └── assets/                        # moved stray PNGs land here
│
├── resources/
│   └── MANIFEST.md                    # NEW — "lecture PDFs/handouts live in Drive (IP)"
│                                      # (binaries removed from tree + history)
│
├── lectures/                          # 01–09 (add 09), author write-ups + demo code
├── homework/                          # hw01–hw06
├── exercises/
│
├── oz_veruach_bot/                    # kept in place this pass; later → own repo (untouched)
│
└── projects/
    ├── README.md
    ├── incident-assistant-rag/        # FEATURED capstone (FastAPI + OpenAI + FAISS)
    ├── incident-rag-bedrock/          # labeled "Bedrock learning iteration"
    └── piter-aiops/  →  README pointer to reem-mor/piter-aiops (after extraction)
```

---

## Split plan — extract `piter-aiops` to its own repo

PITER is **extraction-clean** (no local filesystem coupling; only S3-prefix defaults). Plan:

**Phase A — make it standalone-ready (PR on `amdocs-ai-course`):**
- Polished top-level README (AI Engineer × SRE framing; what PITER is: AWS Bedrock
  incident-response platform — agent + RAG, Flask/React, Docker), architecture diagram,
  screenshots.
- Add `LICENSE`, ensure `.env.example`, `.gitignore`, working `Dockerfile`/`docker-compose`,
  runnable `tests/`, and a minimal CI (`ruff` + `pytest`).
- **Scrub live AWS identifiers** (KB/agent/instance IDs, hostnames) → env placeholders.
- Fix any path/import assuming the monorepo.

**Phase B — extract with history (run locally where `git`+`gh` are authed):**
```bash
gh repo create reem-mor/piter-aiops --public \
  --description "AI-powered incident-response platform: AWS Bedrock agent + RAG, Flask/React, Docker."
git clone https://github.com/reem-mor/amdocs-ai-course.git piter-extract && cd piter-extract
pip install git-filter-repo
git filter-repo --path projects/piter-aiops/ --path-rename projects/piter-aiops/:
git remote add origin https://github.com/reem-mor/piter-aiops.git
git branch -M main && git push -u origin main
```

**Phase C — clean the monorepo:** follow-up PR removing `projects/piter-aiops/` and
replacing it with a one-line README pointer to `reem-mor/piter-aiops`.

---

## Prioritized action plan (P0 / P1 / P2)

### P0 — do first (correctness, IP, credibility)
1. **Re-encode root `requirements.txt` to UTF-8.** (Broken tooling.)
2. **Remove Amdocs copyrighted material** (`resources/` PDFs + handouts) from the tree;
   add `resources/MANIFEST.md` noting originals live in Drive. Document the **history purge**
   in `docs/SECURITY_REMEDIATION.md` (run deliberately, not inside the cleanup PR).
3. **Reframe the root README** as course + learning archive: lead with AI Engineer × SRE,
   accurate repo map, "Featured work" linking OUT to PITER AiOps + HINDSIGHT. Surface lecture
   09, all projects, and `oz_veruach_bot`. Delete the unfounded "hardcoded tokens" caveat.
4. **Untrack + gitignore `.playwright-mcp/`** (89 junk files).

### P1 — strong signal, low risk
5. **Consolidate agent config:** create canonical `AGENTS.md`; `CLAUDE.md` → `@AGENTS.md`;
   de-dupe `.cursor/skills` vs `.agents/skills` to one tree; align Cursor rules.
6. **Clean MCP config:** add minimal `.mcp.json` (n8n, aws-api, bedrock-kb, aws-knowledge,
   playwright, lovable); drop dead servers (context7, sequential-thinking, perplexity); fix
   or drop `course-tools`; drop the `firecrawl` plugin.
7. **Add CI** (`.github/workflows/ci.yml`: ruff + pytest) and a root ruff config → green checks.
8. **Move/remove stray root PNGs**: `reference-*.png` → PITER screenshots (fix refs);
   `current-home.png` → `docs/assets/`; remove `phase0-dashboard-top.png` and orphaned
   `assets/profile-banner.png` (or wire the banner into the README).

### P2 — polish & follow-through
9. **Label `incident-rag-bedrock`** as a Bedrock learning iteration; ensure every kept
   sub-area has a short "what it is / how to run it" README.
10. **Pin Python 3.12** (`.python-version` / per-area) for consistency.
11. **Extract PITER** (Prompt 3, Phases A→B→C) — scrub AWS IDs first.
12. **Later:** extract `oz_veruach_bot` to its own repo (separate pass; internals untouched here).
13. **Manual GitHub steps:** description + topics on every repo, pin best 6 repos, social
    preview images, profile README (`reem-mor/reem-mor`).

---

### Assumptions made (where unsure)
- **Branch:** Per this session's git requirements, the report is committed on
  `claude/github-portfolio-overhaul-ohfpx5` (the designated branch) rather than the plan's
  `audit/portfolio-2026`, to honor "never push to a different branch without permission."
- **HINDSIGHT** is referenced from the About-me block; it is not in this repo, so it's
  treated as an external flagship to link out to.
- **`oz_veruach_bot`** extraction is noted but deferred — the cleanup constraints say not to
  modify its internals, so this pass only documents it and surfaces it in the README.
- History purge is **recommended but not executed** here (read-only audit), and is scoped to
  the **copyrighted binaries**, not secrets (none found).
