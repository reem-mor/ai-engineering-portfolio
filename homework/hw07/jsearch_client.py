"""HTTP client for JSearch (RapidAPI) used by hw07 tools server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

RAPIDAPI_KEY_ENV = "RAPIDAPI_KEY"
RAPIDAPI_HOST_ENV = "RAPIDAPI_HOST"
MOCK_RAPIDAPI_ENV = "HW07_MOCK_RAPIDAPI"
DEFAULT_HOST = "jsearch.p.rapidapi.com"
JSEARCH_SEARCH_PATH = "/search"

_MOCK_JOBS: list[dict[str, Any]] = [
    {
        "job_title": "Senior AI Engineer",
        "employer_name": "Mock Tech IL",
        "job_city": "Tel Aviv",
        "job_country": "Israel",
        "job_apply_link": "https://example.com/jobs/ai-engineer",
        "job_publisher": "mock",
    },
    {
        "job_title": "DevOps Engineer",
        "employer_name": "Mock Cloud IL",
        "job_city": "Herzliya",
        "job_country": "Israel",
        "job_apply_link": "https://example.com/jobs/devops",
        "job_publisher": "mock",
    },
    {
        "job_title": "Machine Learning Engineer",
        "employer_name": "Mock Data IL",
        "job_city": "Jerusalem",
        "job_country": "Israel",
        "job_apply_link": "https://example.com/jobs/ml",
        "job_publisher": "mock",
    },
]


class JSearchNotConfiguredError(Exception):
    """Raised when RAPIDAPI_KEY is missing in live mode."""


class JSearchUpstreamError(Exception):
    """Raised when JSearch HTTP call fails."""


def is_mock_mode() -> bool:
    return os.environ.get(MOCK_RAPIDAPI_ENV, "").strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class JSearchSettings:
    api_key: str
    host: str
    mock_mode: bool

    @classmethod
    def from_env(cls) -> JSearchSettings:
        return cls(
            api_key=os.environ.get(RAPIDAPI_KEY_ENV, "").strip(),
            host=os.environ.get(RAPIDAPI_HOST_ENV, DEFAULT_HOST).strip() or DEFAULT_HOST,
            mock_mode=is_mock_mode(),
        )

    def require_live_credentials(self) -> None:
        if not self.mock_mode and not self.api_key:
            raise JSearchNotConfiguredError(
                f"{RAPIDAPI_KEY_ENV} is not set. Add it to .env for live JSearch calls."
            )

    @property
    def jsearch_configured(self) -> bool:
        return self.mock_mode or bool(self.api_key)


class JSearchClient:
    def __init__(self, settings: JSearchSettings | None = None) -> None:
        self._settings = settings or JSearchSettings.from_env()
        self._http = httpx.Client(timeout=30.0)

    def close(self) -> None:
        self._http.close()

    def search_jobs(
        self,
        query: str,
        location: str = "Israel",
        num_pages: int = 1,
    ) -> list[dict[str, Any]]:
        self._settings.require_live_credentials()

        if self._settings.mock_mode:
            role = query.lower()
            return [
                job
                for job in _MOCK_JOBS
                if role in job["job_title"].lower() or "engineer" in role
            ] or _MOCK_JOBS

        search_query = f"{query} in {location}" if location else query
        params = {
            "query": search_query,
            "page": "1",
            "num_pages": str(min(max(num_pages, 1), 3)),
            "date_posted": "month",
        }
        url = f"https://{self._settings.host}{JSEARCH_SEARCH_PATH}"
        headers = {
            "x-rapidapi-key": self._settings.api_key,
            "x-rapidapi-host": self._settings.host,
            "Accept": "application/json",
        }

        try:
            response = self._http.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise JSearchUpstreamError("JSearch request timed out") from exc
        except httpx.HTTPError as exc:
            raise JSearchUpstreamError(f"JSearch request failed: {exc}") from exc

        if payload.get("status") != "OK":
            message = payload.get("message") or payload.get("error") or "Unknown JSearch error"
            raise JSearchUpstreamError(str(message))

        raw_jobs = payload.get("data") or []
        return [
            {
                "job_title": item.get("job_title"),
                "employer_name": item.get("employer_name"),
                "job_city": item.get("job_city"),
                "job_country": item.get("job_country"),
                "job_apply_link": item.get("job_apply_link"),
                "job_publisher": item.get("job_publisher"),
            }
            for item in raw_jobs
        ]
