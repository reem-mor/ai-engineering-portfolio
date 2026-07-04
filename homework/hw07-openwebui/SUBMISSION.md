# HW07 Submission Guide

## What to submit

- [ ] All files in this folder (see structure in [README.md](README.md))
- [ ] **8 screenshots** in a `screenshots/` folder — see below
- [ ] Short explanation of KB questions vs tool questions (covered by the "Try it" table in the README and screenshots 5–8)

Verified state before submitting:

```text
python -m pytest -v   → 15 passed
ruff check .          → all checks passed
GET /health           → {"status": "ok"}
```

## Screenshots (8)

### Setup proof

| # | File | What it shows |
|---|---|---|
| 1 | `01-tests.png` | Terminal: `python -m pytest -v` output ending in **`15 passed`** |
| 2 | `02-live-api.png` | Browser at `http://localhost:5005/country/France` — JSON with `"success": true` and currency `EUR` (proves server + RapidAPI key work end-to-end) |
| 3 | `03-knowledge-base.png` | Open WebUI → Workspace → Knowledge: **`Netflix Shows KB`** with `netflix_titles.csv` uploaded and indexing complete |
| 4 | `04-tool.png` | Open WebUI → Workspace → Tools: **`Netflix Country Info`** tool saved and **enabled**, code visible |

### Demo chats — exact questions and expected answers

| # | File | Ask this | Expected answer |
|---|---|---|---|
| 5 | `05-chat-kb.png` | `#netflix-shows-kb List 5 Netflix titles from India.` | 5 real titles from the CSV (e.g. *Kota Factory*, *Jeans*, *Chhota Bheem*) with the KB citation visible |
| 6 | `06-chat-tool.png` | `What currency is used in Japan?` | **JPY** — with the tool-call indicator (`get_country_info`) visible in the chat |
| 7 | `07-chat-combined.png` | `#netflix-shows-kb Show 3 Netflix titles from Japan and tell me Japan's currency.` | 3 Japanese titles (e.g. *InuYasha* movies, *Naruto Shippuden the Movie*) **and** JPY — one answer using both sources |
| 8 | `08-chat-edge-case.png` | `What currency is used in Atlantis?` | Assistant says the live country service could not find it — **no invented answer** (server returns `404`) |

Screenshots 5–7 map directly to the three assignment capabilities: KB-only, tool-only, combined. Screenshot 8 shows error handling.

> Tip: capture each chat so the question, the answer, and the KB citation / tool indicator are all in frame.
