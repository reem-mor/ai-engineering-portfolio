# PITER AiOps — extraction-ready

> **Status:** This copy lives in the course archive until [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) is created and verified. The external repo does **not** exist yet (link will 404 until you push).

## Why extract

Flagship agentic incident-response platform (Bedrock Agent + RAG + tools). It has its own test suite (~325 tests), Docker stack, and deployment docs. It should not share git history with homework notebooks.

## Pre-flight checklist

- [ ] Parameterize live AWS identifiers (EC2 instance ID, public hostname, Bedrock agent/KB IDs) in docs — see [`docs/SECURITY_REMEDIATION.md`](../../docs/SECURITY_REMEDIATION.md)
- [ ] Run `py -3.12 -m pytest -q` from this directory
- [ ] Run `cd frontend && npm ci && npm run build` (SPA is gitignored here)
- [ ] Confirm no `.env` or keys in the tree

## Extract (option A — subtree split, preserves history)

From the archive repo root:

```powershell
# See scripts/extract-piter-aiops.ps1 for the full scripted flow
git subtree split --prefix=projects/piter-aiops -b piter-aiops-split
mkdir ..\piter-aiops-export
git clone . ..\piter-aiops-export --branch piter-aiops-split --single-branch
cd ..\piter-aiops-export
# Move contents from projects/piter-aiops/ to repo root if needed — script handles this
```

## Extract (option B — clean copy)

```powershell
.\scripts\extract-piter-aiops.ps1 -OutputDir ..\piter-aiops-export
```

## After push to GitHub

1. Enable CI on the new repo (ruff + pytest).
2. In **this** archive, replace `projects/piter-aiops/` with a pointer README linking to the live repo.
3. Update root [`README.md`](../../README.md) Featured work table (remove "extraction in progress").

Templates for the new repo: [`docs/extraction/piter-aiops/`](../../docs/extraction/piter-aiops/).
