# Project extraction guide

Some folders in this archive are **standalone products** that belong in their own
GitHub repositories. This directory holds extraction runbooks, subtree-split commands, and
README/AGENTS stubs for the target repos.

| Source path | Target repo | Status |
|-------------|-------------|--------|
| [`projects/piter-aiops/`](../../projects/piter-aiops/) | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) | **Extraction-ready** — target repo not created yet |
| [`oz_veruach_bot/`](../../oz_veruach_bot/) | [reem-mor/oz-veruach-bot](https://github.com/reem-mor/oz-veruach-bot) | **Extraction-ready** — target repo not created yet |

## Workflow

1. Read the per-project [`EXTRACTION.md`](../../projects/piter-aiops/EXTRACTION.md) in the source folder.
2. Run the matching script under [`scripts/`](../scripts/) (or use the documented `git subtree split` commands).
3. Create the empty GitHub repo, push the split branch, verify CI.
4. In **this** archive: replace the folder with a short pointer (link + one paragraph) once the external repo is live — do not half-delete before the target exists.

Stubs for new repos:

- [`piter-aiops/`](piter-aiops/) — README + AGENTS templates
- [`oz-veruach-bot/`](oz-veruach-bot/) — README + AGENTS templates

## What stays in this archive

- `lectures/`, `homework/`, `exercises/` — course learning archive (your authored work)
- [`projects/incident-assistant-rag/`](../projects/incident-assistant-rag/) — featured capstone (OpenAI + local FAISS)
- [`projects/incident-rag-bedrock/`](../projects/incident-rag-bedrock/) — labeled **learning iteration** (Bedrock KB stepping-stone)
