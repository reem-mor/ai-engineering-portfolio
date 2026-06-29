# Project extraction guide

Standalone products that lived in this archive now have their own GitHub repositories.
This directory holds extraction runbooks and README/AGENTS stubs used during the split.

| Former path | Target repo | Status |
|-------------|-------------|--------|
| `projects/piter-aiops/` | [reem-mor/piter-aiops](https://github.com/reem-mor/piter-aiops) | **Extracted** — pointer at [`projects/piter-aiops/README.md`](../../projects/piter-aiops/README.md) |
| `oz_veruach_bot/` | [reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) | **Extracted** — pointer at [`course-assistant-bot/README.md`](../../course-assistant-bot/README.md) |

## Re-export (if needed)

```powershell
.\scripts\extract-piter-aiops.ps1 -CleanCopy -OutputDir C:\dev\piter-aiops
.\scripts\extract-course-assistant-bot.ps1 -CleanCopy -OutputDir C:\dev\course-assistant-bot
```

## What stays in this archive

- `lectures/`, `homework/`, `exercises/` — course learning archive
- [`projects/incident-assistant-rag/`](../projects/incident-assistant-rag/) — featured capstone (OpenAI + local FAISS)
- [`projects/incident-rag-bedrock/`](../projects/incident-rag-bedrock/) — labeled **learning iteration** (Bedrock KB stepping-stone)

Stubs for target repos: [`piter-aiops/`](piter-aiops/) · [`course-assistant-bot/`](course-assistant-bot/).
