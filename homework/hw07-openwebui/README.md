# Netflix KB + Local Tool Server Homework

## Overview
This project demonstrates two assistant capabilities:

1. **Knowledge Base (KB)** using a Kaggle CSV uploaded into Open WebUI.
2. **Local Python Tool Server** that calls an external API through RapidAPI.

The assistant can:
- answer dataset questions using the uploaded KB
- answer live country questions using the local Python server

---

## Dataset
**Dataset:** Netflix Movies and TV Shows  
**Source:** Kaggle  
**Link:** https://www.kaggle.com/datasets/shivamb/netflix-shows

This dataset includes fields such as:
- `show_id`
- `type`
- `title`
- `director`
- `cast`
- `country`
- `date_added`
- `release_year`
- `rating`
- `duration`
- `listed_in`
- `description`

---

## External API
**API used:** Country State City - Search REST API  
**Source:** RapidAPI  
**Plan:** Free Basic tier

This API is relevant because the Netflix dataset contains a `country` field, so the assistant can combine dataset questions with live country information.

Example:
- KB question: "List 5 Netflix titles from France"
- Tool question: "What currency is used in France?"

The RapidAPI `/allcountries` payload includes fields such as `name`, `isoCode`, `currency`, `phonecode`, `latitude`, `longitude`, `flag`, and `timezones`. It does not include capital or region.

---

## Project Structure

```text
hw07-openwebui/
├── README.md
├── requirements.txt
├── .env.example
├── tools_server.py
├── test_tools_server.py
├── system_prompt.txt
├── openwebui_function_tool.py
├── screenshots_checklist.md
└── data/
    ├── download_dataset.py
    └── netflix_titles.csv
```

---

## Setup

### 1. Install dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Download dataset (optional if CSV already present)
Requires Kaggle CLI credentials (`kaggle.json` or `KAGGLE_USERNAME` / `KAGGLE_KEY`):

```powershell
python data/download_dataset.py
```

### 3. Create environment file
Copy `.env.example` and create your own `.env` file in this folder:

```powershell
Copy-Item .env.example .env
```

Then add your RapidAPI key:
```env
RAPIDAPI_KEY=your_real_rapidapi_key_here
```

The server loads only `homework/hw07-openwebui/.env` (not the repo root `.env`).

### 4. Run the local server
```powershell
python tools_server.py
```

The server runs on:
```text
http://localhost:5005
```

### 5. Run tests
```powershell
python -m pytest -v
```

---

## Open WebUI KB Setup

1. Open Open WebUI.
2. Go to **Workspace** -> **Knowledge**.
3. Create a new Knowledge Base called `Netflix Shows KB`.
4. Upload `data/netflix_titles.csv`.
5. Wait until indexing is complete.
6. Use this KB in your chat/model.

---

## Open WebUI Tool Setup

1. Go to **Workspace** -> **Tools** or **Functions**.
2. Create a new tool/function.
3. Copy the code from `openwebui_function_tool.py`.
4. Save and enable the tool.
5. Make sure your local Flask server is running on `http://localhost:5005`.

---

## System Prompt

Use the content from `system_prompt.txt` in your model or chat system prompt.

Purpose:
- use KB for dataset questions
- use tool for live country questions
- combine both when needed

---

## Local Server Endpoints

### `GET /health`
Checks if the local server is running.

### `GET /country/<country_name>`
Returns country information from RapidAPI.

---

## Sample Questions and Expected Behavior

### KB questions
These should be answered from the uploaded CSV:
- List 5 Netflix titles from India.
- Which titles were released in 2020?
- What ratings appear most often in the dataset?
- Show movies from the United States.

### Tool questions
These should use the local Python server:
- What currency is used in Japan?
- What is the ISO code for France?
- What phone code is used in Brazil?
- Give me country details for Canada.

### Combined questions
These can use both KB and tool:
- Show 3 Netflix titles from Japan and tell me Japan's currency.
- List Netflix titles from France and give me France's currency.

---

## Submission

Submit:
- all project files
- screenshots listed in `screenshots_checklist.md`
- explanation of KB questions vs tool questions
