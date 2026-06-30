# Security Remediation

Status as of the 2026 portfolio cleanup. See [`AUDIT_2026.md`](AUDIT_2026.md) for the full
audit. This file is the deliberate-action runbook — history rewrites are **not** performed
automatically; run them yourself when ready.

## 1. Secrets — current status: clean

A full scan of the **working tree** and **complete git history** (all branches/remotes) for
provider-key patterns (`sk-`, `sk-ant-`, `AKIA`, `ghp_`, `hf_`, `AIza`, `xoxb-`/`xoxp-`),
private-key blocks, and generic `api_key`/`token`/`password` assignments found:

> **Zero real secrets.** No `.env`, `*.pem`, or `*.key` file was ever committed. Every match
> resolved to a placeholder (`your_..._here`), a documentation example, an env-var reference
> (`${env:...}`), an AWS named profile, an SSM parameter path name, or a runtime accessor.

**Action required: none for secrets.** If any service was ever used locally with a real key,
rotate it as routine hygiene, but nothing is exposed in this repository.

## 2. Live AWS identifiers (fix before public extraction of PITER)

PITER docs/config embed live, account-specific identifiers — **not credentials**, but they
reveal infrastructure topology and should be parameterized before the project goes public:

- Bedrock Knowledge Base ID, Bedrock Agent ID
- EC2 instance ID, public EC2 hostname(s)

**Action:** during PITER standalone prep, replace these with `${ENV_VAR}` placeholders backed
by `.env.example`. Track them as environment configuration, not literals in tracked files.

## 3. Git-history size — purge the removed course binaries (optional but recommended)

The Amdocs lecture PDFs and handouts were removed from the working tree (see
[`resources/MANIFEST.md`](../resources/MANIFEST.md)), but they remain in history, so `.git`
is still large (**~229 MB** on disk as of 2026-06-29; clone size unchanged by untracking
build artifacts alone). To reclaim space and stop redistributing the binaries via history,
rewrite history deliberately on a fresh clone, then force-push.

> ⚠️ History rewrite. Coordinate first (it changes commit hashes); take a backup clone.

### Option A — git-filter-repo (recommended)

```bash
git clone https://github.com/reem-mor/ai-engineering-portfolio.git ai-engineering-portfolio-clean
cd amdocs-clean
pip install git-filter-repo

# Drop the course-material binaries from ALL history:
git filter-repo --invert-paths \
  --path-glob 'resources/*.pdf' \
  --path-glob 'resources/handouts/*.docx' \
  --path-glob 'resources/handouts/*.pptx'

# Also drop the accidentally-committed Playwright snapshots from history:
git filter-repo --invert-paths --path .playwright-mcp

git remote add origin https://github.com/reem-mor/ai-engineering-portfolio.git
git push --force-with-lease --all origin
git push --force-with-lease --tags origin
```

### Option B — BFG Repo-Cleaner

```bash
bfg --delete-files '*.{pdf,pptx,docx}' --no-blob-protection
bfg --delete-folders '.playwright-mcp'
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push --force-with-lease --all origin
```

After either option: re-clone fresh and confirm `.git` shrank and the binaries are gone
(`git log --all --oneline -- 'resources/*.pdf'` returns nothing).

## 4. Keys to rotate

None mandated by the scan. Rotate only as routine hygiene if a real key was ever used
locally with one of the placeholder-named services (OpenAI, Gemini, Hugging Face, n8n).

## 5. Verification checklist

- [ ] `git status` shows no `.env` / key-bearing files before any commit.
- [ ] `.gitignore` covers `.env`, `.cursor/mcp.json`, credential JSON, `*.pem`, `*.key`,
      `.playwright-mcp/`, FAISS, `*.sqlite`, `node_modules`, `.venv` — confirmed.
- [ ] PITER live AWS identifiers parameterized before public extraction.
- [ ] (Optional) history purge run; `.git` size reduced; binaries gone from history.
