# HW07 — Test questions and expected outputs

Run these in Open WebUI against the model that has the **AI Job Market Intelligence
Dataset** KB attached and the **ai_job_market_live_search** tool enabled.
Fill in *Actual output summary* and *Pass/Fail* during the local demo.

Negative tests marked ✅ were executed offline against the tool server in CI-style
tests (`pytest tests/`) — their actual results are recorded below.

## 1. KB-only questions (Kaggle dataset)

| # | Input question | Expected behavior | Actual output summary | Pass/Fail |
|---|----------------|-------------------|-----------------------|-----------|
| KB-1 | What are the most common AI job titles in the Kaggle dataset? | Answer from KB; cites dataset (job_title counts); says source = Kaggle dataset | | |
| KB-2 | Which skills appear most often in the dataset? | Aggregates `required_skills` from KB; source = Kaggle dataset | | |
| KB-3 | What countries or locations appear most often? | Uses `company_location` / `employee_residence`; source = Kaggle dataset | | |
| KB-4 | What salary trends can you summarize from the dataset? | Summarizes `salary_usd` by experience level / year; no invented numbers; source = Kaggle dataset | | |

## 2. Tool-only questions (live RapidAPI)

| # | Input question | Expected behavior | Actual output summary | Pass/Fail |
|---|----------------|-------------------|-----------------------|-----------|
| T-1 | Search live AI Engineer jobs in Israel. | Calls `search_jobs(query="AI Engineer", location="Israel")`; lists real postings; source = live RapidAPI tool | | |
| T-2 | Search live DevOps Engineer jobs in Tel Aviv. | Calls tool with location "Tel Aviv"; source = live tool | | |
| T-3 | Search live Machine Learning Engineer jobs in London. | Calls tool with location "London"; source = live tool | | |
| T-4 | Search live jobs that mention Python. | Calls `search_jobs_by_skill(skill="Python")`; source = live tool | | |

## 3. Mixed KB + tool questions

| # | Input question | Expected behavior | Actual output summary | Pass/Fail |
|---|----------------|-------------------|-----------------------|-----------|
| M-1 | Compare the Kaggle dataset trends with live AI Engineer jobs in Israel. | Uses BOTH; clearly labels which claims come from KB vs live tool | | |
| M-2 | Based on the dataset and live jobs, what skills should I learn for AI Engineer roles? | KB skill frequencies + live posting requirements; labels both sources | | |
| M-3 | Are salary or role trends in the dataset similar to current live job listings? | Compares KB salary stats with live postings; notes live postings often omit salary; labels sources | | |

## 4. Negative tests

| # | Input | Expected behavior | Actual output summary | Pass/Fail |
|---|-------|-------------------|-----------------------|-----------|
| N-1 | `GET /jobs/search` (missing query) | HTTP 422, JSON `error: "Parameter 'query' must not be empty."`, `count: 0` | 422 + clean error JSON (offline pytest) | ✅ Pass |
| N-2 | `GET /jobs/search?query=ai&location=<101+ chars>` (invalid location) | HTTP 422, clean error, no upstream call | 422 + clean error JSON (offline pytest) | ✅ Pass |
| N-3 | RapidAPI key missing | HTTP 503, `error` says RAPIDAPI_KEY not configured; key never printed | 503 + clean error JSON (offline pytest) | ✅ Pass |
| N-4 | RapidAPI timeout | HTTP 504, `error: "Upstream RapidAPI request timed out..."` | 504 + clean error JSON (offline pytest, mocked timeout) | ✅ Pass |
| N-5 | KB has no attached files | Assistant answers without dataset grounding and says the KB is empty / falls back; `owui_kb_setup.py` verification exits 1 | | |
| N-6 | Tool server down | Open WebUI tool returns `error: "Local tool server unreachable..."`; assistant explains failure and continues KB-only | | |
