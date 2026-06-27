# GitHub Profile Playbook — 2026 employer-ready

Run these on your own machine where `git` and `gh` are authenticated
(`gh auth login`). This session's automation is scoped to `amdocs-ai-course` only, so the
repo-creation, topics, pinning, and extraction steps below are for you to run. Each is copy-paste.

> Order: **1 → 2 → 3 → 4 → 5**. Steps 1 and 3 give the biggest visible payoff.

---

## 1. Publish the profile README (highest leverage)

The repo named exactly after your username renders its README on your profile page.

```bash
# From anywhere
gh repo create reem-mor/reem-mor --public --description "Profile README — AI Engineer × SRE" --clone
cd reem-mor

# Copy the staged README from this repo (adjust the path to where you cloned amdocs-ai-course)
cp ../amdocs-ai-course/docs/portfolio/profile-README.md README.md

# IMPORTANT: edit README.md and replace the LinkedIn placeholder URL (REPLACE-ME)
$EDITOR README.md

git add README.md
git commit -m "Add profile README"
git push -u origin main
```

Visit https://github.com/reem-mor — the README now shows on your profile.

---

## 2. Descriptions + topics on every repo

Clean descriptions and topics make repos discoverable and look intentional. Suggested topics:
`ai-engineering`, `rag`, `aws-bedrock`, `llm`, `agents`, `incident-response`, `sre`,
`python`, `docker`, `automation`.

```bash
# amdocs-ai-course
gh repo edit reem-mor/amdocs-ai-course \
  --description "AI-Augmented Software Engineering coursework & learning archive — RAG, agents, full-stack AI. By an AI Engineer × SRE." \
  --add-topic ai-engineering --add-topic rag --add-topic llm --add-topic python \
  --add-topic fastapi --add-topic docker --add-topic sre

# piter-aiops  (after step 3 creates it)
gh repo edit reem-mor/piter-aiops \
  --description "AI-powered incident-response platform: AWS Bedrock agent + RAG, Flask/React, Docker. Built by an AI Engineer × SRE." \
  --add-topic ai-engineering --add-topic aws-bedrock --add-topic rag --add-topic agents \
  --add-topic incident-response --add-topic sre --add-topic python --add-topic docker

# hindsight
gh repo edit reem-mor/hindsight \
  --description "Intelligent incident-log / document analyst with semantic search — grounded answers over operational history." \
  --add-topic ai-engineering --add-topic rag --add-topic semantic-search --add-topic llm --add-topic python

# oz_veruach_bot  (if/when public)
gh repo edit reem-mor/oz_veruach_bot \
  --description "Bilingual (HE/EN) async Telegram assistant — SQLAlchemy + Alembic, multi-LLM, Docker. Strict typing, 200+ tests." \
  --add-topic telegram-bot --add-topic python --add-topic asyncio --add-topic llm
```

Repeat the pattern for any other repos worth keeping; archive or make private the ones that
don't represent you (old throwaways dilute a profile).

---

## 3. Extract PITER AiOps into its own repo (with history)

PITER is the flagship and reads better as a standalone repo. Step A (making it
self-contained: LICENSE, `.env.example`, scrubbed AWS identifiers, staged CI) is already
done inside `projects/piter-aiops/` in this repo. Now extract it:

```bash
# 3a. Create the empty repo
gh repo create reem-mor/piter-aiops --public \
  --description "AI-powered incident-response platform: AWS Bedrock agent + RAG, Flask/React, Docker."

# 3b. Extract the subfolder WITH history, moved to the new repo root
git clone https://github.com/reem-mor/amdocs-ai-course.git piter-extract
cd piter-extract
pip install git-filter-repo
git filter-repo --path projects/piter-aiops/ --path-rename projects/piter-aiops/:

# 3c. The staged CI lives at .github/workflows/ci.yml after the rename — confirm it's there
ls .github/workflows/

# 3d. Push to the new repo
git remote add origin https://github.com/reem-mor/piter-aiops.git
git branch -M main
git push -u origin main
```

**3e. Clean the monorepo** — after verifying the new repo builds, open a PR on
`amdocs-ai-course` that removes `projects/piter-aiops/` and replaces it with a one-line
README pointer to `reem-mor/piter-aiops`. (Ask this assistant to do that PR in a new session.)

> The README links in `amdocs-ai-course` and the profile already point to
> `github.com/reem-mor/piter-aiops`, so they go live the moment this push completes.

---

## 4. Pin your best repos

Profile → **Customize your pins** → select up to 6, in this order:

1. **piter-aiops** (flagship)
2. **hindsight**
3. **amdocs-ai-course** (archive — shows range + CI)
4. oz_veruach_bot (if public)
5. + 2 more of your strongest

Pins are the first thing a reviewer scans — lead with the flagships.

---

## 5. Social preview + final polish (per flagship repo)

For **piter-aiops** and **hindsight**:

- **Settings → Social preview** → upload a 1280×640 image (a clean architecture diagram or a
  product screenshot with the project name). Makes shared links look sharp.
- Confirm each has: README with **screenshots + architecture diagram**, **LICENSE**, a
  **green CI badge**, and a live-demo link if one exists.
- **HINDSIGHT specifically:** apply the same standard as PITER — README leading with the
  AI Engineer × SRE framing, `.env.example`, `.gitignore`, Dockerfile, a `tests/` suite, and
  a minimal `ruff + pytest` CI workflow. (Happy to do this in a session scoped to that repo.)

---

## 6. Security sign-off before promoting the profile

- Confirm no secrets remain in any flagship's history (`amdocs-ai-course` is already clean —
  see `docs/SECURITY_REMEDIATION.md`).
- **Rotate** any key that was ever used locally with a placeholder-named service, as hygiene.
- Confirm PITER's live AWS identifiers are parameterized (done in Step A) before the repo is
  public-facing.

---

### What's already done for you (in `amdocs-ai-course`)

- ✅ Repo reframed as a course/learning archive; README leads with AI Engineer × SRE.
- ✅ Copyrighted course material removed; CI (ruff + pytest) green; tooling fixed.
- ✅ Agent/MCP config consolidated; secrets audit clean.
- ✅ PITER made standalone-ready (LICENSE, scrubbed AWS IDs, staged CI) — ready for step 3.
- ✅ Profile README drafted (`docs/portfolio/profile-README.md`) — ready for step 1.
