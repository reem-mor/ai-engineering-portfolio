# course-assistant-bot

**This project now lives in its own repository.**

| | |
|---|---|
| **Repo** | [github.com/reem-mor/course-assistant-bot](https://github.com/reem-mor/course-assistant-bot) |
| **What** | Bilingual (HE/EN) Telegram course-ops bot — schedule, recordings, homework, RAG recommendations, admin flows |
| **Stack** | Python 3.12 · uv · SQLAlchemy/Alembic · multi-LLM · Docker · strict typing · 200+ mocked tests |

Former path in this archive: `oz_veruach_bot/` (removed after extraction).

```bash
git clone https://github.com/reem-mor/course-assistant-bot.git
cd course-assistant-bot
uv sync --extra dev && cp .env.example .env
uv run pytest -q
```
