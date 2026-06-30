# Project extraction guide

Standalone products that lived in this archive now have their own GitHub repositories.
This directory holds extraction runbooks and README/AGENTS stubs used during the split.

| Former path | Target repo | Status |
|-------------|-------------|--------|
| `projects/piter-aiops/` | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) | **Extracted** — [`flagships/piter-aiops/README.md`](../../flagships/piter-aiops/README.md) |
| `oz_veruach_bot/` | [reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) | **Extracted** — [`flagships/course-assistant-bot/README.md`](../../flagships/course-assistant-bot/README.md) |
| — | [reem-mor/hindsight](https://github.com/reem-mor/hindsight) | **External** — [`flagships/hindsight/README.md`](../../flagships/hindsight/README.md) |

Index: [`flagships/README.md`](../../flagships/README.md)

## Re-export (clone from external repos)

Source trees no longer live in this archive.

```powershell
.\scripts\extract-piter-aiops.ps1 -OutputDir C:\dev\piter-aiops
.\scripts\extract-course-assistant-bot.ps1 -OutputDir C:\dev\course-assistant-bot
```

## What stays in this archive

- `lectures/`, `homework/`, `exercises/` — course learning archive
- [`projects/incident-assistant-rag/`](../projects/incident-assistant-rag/) — featured capstone
- [`projects/incident-rag-bedrock/`](../projects/incident-rag-bedrock/) — Bedrock KB learning iteration
- [`flagships/`](../flagships/) — README pointers to external repos

Stubs for target repos: [`piter-aiops/`](piter-aiops/) · [`course-assistant-bot/`](course-assistant-bot/).
