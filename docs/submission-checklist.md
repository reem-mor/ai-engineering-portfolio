# Submission Checklist

Use this before pushing homework or project work for course review.

## Code and runtime

- [ ] Code runs locally from a clean clone (document any extra setup in folder README)
- [ ] Virtual environment created and dependencies installed (`pip install -r requirements.txt` or project-specific file)
- [ ] Tests pass where applicable (`python -m pytest`)
- [ ] No hard-coded API keys or passwords in source files
- [ ] `.env` is local only and listed in `.gitignore`

## Docker (if assignment uses containers)

- [ ] `docker build` succeeds (or document known WIP state, e.g. hw04)
- [ ] Container starts and serves expected endpoint
- [ ] `.dockerignore` excludes venv, cache, and secrets

## Documentation

- [ ] Folder README explains what the assignment does and how to run it
- [ ] Root or project README updated if structure changed
- [ ] Architecture or design decisions documented for larger projects
- [ ] Screenshots included for labs that require evidence (EC2, UI flows)

## Git hygiene

- [ ] `git status` shows only intended files
- [ ] No `.env`, `.pem`, `.key`, `.sqlite`, or `.db` files staged
- [ ] No `__pycache__/`, `.venv/`, `node_modules/`, or build artifacts staged
- [ ] Commit message is clear (e.g. `hw05: EC2 Docker nginx lab evidence`)

## Homework-specific

| HW | Extra checks |
|----|--------------|
| 01 | Notebook runs top-to-bottom |
| 02 | Python scripts execute without errors |
| 03 | `pytest` passes in `homework/hw03/` |
| 04 | Matches RAG handout requirements (topic, FAISS, UI, validation) |
| 05 | EC2 lab screenshots + SUBMISSION.md complete |

## RAG / AI projects

- [ ] Knowledge base indexed before querying
- [ ] Grounded answers cite sources when context exists
- [ ] Irrelevant questions return refusal / no-context behavior
- [ ] Evaluation questions documented (where required)

## Pre-push verification commands

```powershell
git status
git diff --stat
git ls-files | findstr /i ".env key pem db sqlite"
python -m pytest
```

## References

- Submission workflow: [`CONTRIBUTING.md`](../CONTRIBUTING.md)
- Setup: [`docs/setup.md`](setup.md)
- Course handouts: [`resources/handouts/`](../resources/handouts/)
