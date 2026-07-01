"""
title: ai_job_market_live_search
description: Search current AI, ML, DevOps, SRE, and software engineering jobs using RapidAPI via the local hw07 tool server.
version: 2.0.0
license: MIT
"""

# Open WebUI Tool — paste this file's content into:
#   Open WebUI > Workspace > Tools > + Create Tool  (ID: ai_job_market_live_search)
# then enable the tool on your model (Workspace > Models > edit > Tools).
#
# Alternative (preferred, zero-copy): register the tool server directly as an
# OpenAPI tool at http://host.docker.internal:5005/openapi.json
# (Admin > Settings > External Tools). Both call the same local server.
#
# No secrets here: the RapidAPI key stays in the repo root .env, read only by
# tools_server.py.

import json

import requests
from pydantic import BaseModel, Field

TIMEOUT_S = 20


class Tools:
    class Valves(BaseModel):
        tools_server_url: str = Field(
            default="http://host.docker.internal:5005",
            description=(
                "Base URL of the local hw07 tool server "
                "(use http://localhost:5005 if Open WebUI runs on the host)."
            ),
        )

    def __init__(self):
        self.valves = self.Valves()

    def _get(self, path: str, params: dict) -> str:
        base = self.valves.tools_server_url.rstrip("/")
        try:
            response = requests.get(f"{base}{path}", params=params, timeout=TIMEOUT_S)
            return json.dumps(response.json())
        except requests.Timeout:
            return json.dumps(
                {"error": f"Local tool server timed out after {TIMEOUT_S}s.", "results": []}
            )
        except (requests.RequestException, ValueError) as exc:
            return json.dumps(
                {
                    "error": f"Local tool server unreachable at {base}: {exc.__class__.__name__}",
                    "results": [],
                }
            )

    def search_jobs(self, query: str, location: str = "") -> str:
        """
        Search CURRENT live job postings (AI, ML, DevOps, SRE, software) by
        role/keywords and optional location. Use this for questions about jobs
        open right now; use the knowledge base for the static Kaggle dataset.

        :param query: Job search terms, e.g. "AI engineer".
        :param location: Optional location, e.g. "Israel" or "Tel Aviv".
        :return: JSON string with source, query, count, results, and error if any.
        """
        return self._get("/jobs/search", {"query": query, "location": location})

    def search_jobs_by_company(self, company: str) -> str:
        """
        Search current live job postings at a specific company.

        :param company: Company name, e.g. "Google".
        :return: JSON string with source, query, count, results, and error if any.
        """
        return self._get("/jobs/company", {"company": company})

    def search_jobs_by_skill(self, skill: str) -> str:
        """
        Search current live job postings that mention a specific skill.

        :param skill: Skill keyword, e.g. "Python" or "Kubernetes".
        :return: JSON string with source, query, count, results, and error if any.
        """
        return self._get("/jobs/skills", {"skill": skill})
