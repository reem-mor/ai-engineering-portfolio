# Oz Veruach Bot — extraction-ready

> **Status:** Standalone bilingual Telegram product. Stays in this monorepo until [reem-mor/oz-veruach-bot](https://github.com/reem-mor/oz-veruach-bot) is created. Target repo does **not** exist yet.

## Why extract

Zero coupling to course projects — separate product (`uv`, strict typing, Alembic, own CI). Per archive policy: **do not refactor internals** during extraction; copy out as-is.

## Pre-flight checklist

- [ ] Run tests with project venv: `uv run pytest` (from this directory)
- [ ] Confirm `.env` is gitignored; only `.env.example` committed
- [ ] Review [`README.md`](README.md) for deployment secrets

## Extract

```powershell
# From archive repo root
.\scripts\extract-oz-veruach-bot.ps1 -OutputDir ..\oz-veruach-bot-export
```

Or subtree split:

```powershell
git subtree split --prefix=oz_veruach_bot -b oz-veruach-bot-split
git clone . ..\oz-veruach-bot-export --branch oz-veruach-bot-split --single-branch
```

## After push to GitHub

1. Point root [`README.md`](../README.md) Oz section to the external repo.
2. Replace this folder with a short pointer file (keep one paragraph + link).

Templates: [`docs/extraction/oz-veruach-bot/`](../docs/extraction/oz-veruach-bot/).
