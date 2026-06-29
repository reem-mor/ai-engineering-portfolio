"""HTTP client for RapidAPI endpoints used by the hw07 Open WebUI tool server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

RAPIDAPI_KEY_ENV = "RAPIDAPI_KEY"
MOCK_RAPIDAPI_ENV = "HW07_MOCK_RAPIDAPI"
OMDB_HOST_ENV = "RAPIDAPI_OMDB_HOST"
COUNTRIES_HOST_ENV = "RAPIDAPI_COUNTRIES_HOST"
STREAMING_HOST_ENV = "RAPIDAPI_STREAMING_HOST"

DEFAULT_OMDB_HOST = "imdb8.p.rapidapi.com"
DEFAULT_COUNTRIES_HOST = "restcountries-v1.p.rapidapi.com"
DEFAULT_STREAMING_HOST = "streaming-availability.p.rapidapi.com"

_MOCK_COUNTRY_FIXTURES: dict[str, dict[str, Any]] = {
    "brazil": {
        "name": "Brazil",
        "capital": "Brasília",
        "region": "Americas",
        "population": 212559417,
    },
    "japan": {
        "name": "Japan",
        "capital": "Tokyo",
        "region": "Asia",
        "population": 125836021,
    },
    "germany": {
        "name": "Germany",
        "capital": "Berlin",
        "region": "Europe",
        "population": 83240525,
    },
}


class RapidApiNotConfiguredError(Exception):
    """Raised when RAPIDAPI_KEY is missing."""


def is_mock_mode() -> bool:
    """Return True when deterministic mock responses are enabled (local E2E / screenshots)."""
    return os.environ.get(MOCK_RAPIDAPI_ENV, "").strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class RapidApiSettings:
    api_key: str
    omdb_host: str
    countries_host: str
    streaming_host: str

    @classmethod
    def from_env(cls) -> RapidApiSettings:
        api_key = os.environ.get(RAPIDAPI_KEY_ENV, "").strip()
        if not api_key and not is_mock_mode():
            raise RapidApiNotConfiguredError(
                f"{RAPIDAPI_KEY_ENV} is not set. Add it to .env for live API calls."
            )
        return cls(
            api_key=api_key or "mock",
            omdb_host=os.environ.get(OMDB_HOST_ENV, DEFAULT_OMDB_HOST).strip(),
            countries_host=os.environ.get(COUNTRIES_HOST_ENV, DEFAULT_COUNTRIES_HOST).strip(),
            streaming_host=os.environ.get(STREAMING_HOST_ENV, DEFAULT_STREAMING_HOST).strip(),
        )


class RapidApiClient:
    """Fakeable seam for outbound RapidAPI calls."""

    def __init__(
        self,
        settings: RapidApiSettings,
        *,
        timeout: float = 15.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._timeout = timeout
        self._transport = transport

    def _headers(self) -> dict[str, str]:
        return {
            "X-RapidAPI-Key": self._settings.api_key,
            "X-RapidAPI-Host": "",
        }

    def _request(
        self,
        *,
        host: str,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        headers = self._headers()
        headers["X-RapidAPI-Host"] = host
        url = f"https://{host}{path}"
        with httpx.Client(timeout=self._timeout, transport=self._transport) as client:
            response = client.request(method, url, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload
            return {"data": payload}

    def search_title(self, title: str) -> dict[str, Any]:
        """Search IMDb-style metadata for a Netflix title."""
        if is_mock_mode():
            return {
                "results": [
                    {
                        "title": title,
                        "year": 2021,
                        "mock": True,
                    }
                ]
            }
        return self._request(
            host=self._settings.omdb_host,
            method="GET",
            path="/auto-complete",
            params={"q": title},
        )

    def country_info(self, country_name: str) -> dict[str, Any]:
        """Fetch country facts (capital, region, population)."""
        slug = country_name.strip().lower()
        if is_mock_mode():
            fixture = _MOCK_COUNTRY_FIXTURES.get(slug)
            if fixture:
                return {**fixture, "mock": True}
            return {
                "name": country_name.strip().title(),
                "capital": "Unknown",
                "region": "Unknown",
                "mock": True,
            }
        return self._request(
            host=self._settings.countries_host,
            method="GET",
            path=f"/name/{slug}",
        )

    def streaming_status(self, title: str, country_code: str) -> dict[str, Any]:
        """Check streaming availability for a title in a country (ISO 3166-1 alpha-2)."""
        if is_mock_mode():
            return {
                "result": [
                    {
                        "title": title,
                        "country": country_code.strip().upper(),
                        "streamingOptions": [{"service": "netflix", "mock": True}],
                    }
                ],
                "mock": True,
            }
        return self._request(
            host=self._settings.streaming_host,
            method="GET",
            path="/shows/search/title",
            params={
                "title": title,
                "country": country_code.strip().upper(),
                "output_language": "en",
            },
        )
