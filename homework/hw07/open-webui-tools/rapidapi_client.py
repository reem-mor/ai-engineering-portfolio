"""HTTP client for RapidAPI endpoints used by the hw07 Open WebUI tool server."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

RAPIDAPI_KEY_ENV = "RAPIDAPI_KEY"
MOCK_RAPIDAPI_ENV = "HW07_MOCK_RAPIDAPI"
OMDB_HOST_ENV = "RAPIDAPI_OMDB_HOST"
COUNTRIES_HOST_ENV = "RAPIDAPI_COUNTRIES_HOST"
STREAMING_HOST_ENV = "RAPIDAPI_STREAMING_HOST"

DEFAULT_OMDB_HOST = "imdb8.p.rapidapi.com"
DEFAULT_COUNTRIES_HOST = "restcountries.p.rapidapi.com"
DEFAULT_STREAMING_HOST = "streaming-availability.p.rapidapi.com"

ISO_ALPHA2 = re.compile(r"^[A-Za-z]{2}$")

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
    "united states": {
        "name": "United States",
        "capital": "Washington, D.C.",
        "region": "Americas",
        "population": 331002651,
    },
}


class RapidApiNotConfiguredError(Exception):
    """Raised when RAPIDAPI_KEY is missing."""


class RapidApiNotFoundError(Exception):
    """Raised when upstream returns no matching records."""


class RapidApiUpstreamError(Exception):
    """Raised when upstream HTTP call fails."""


def is_mock_mode() -> bool:
    """Return True when deterministic mock responses are enabled (local E2E / screenshots)."""
    return os.environ.get(MOCK_RAPIDAPI_ENV, "").strip().lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class RapidApiSettings:
    api_key: str
    omdb_host: str
    countries_host: str
    streaming_host: str
    mock_mode: bool

    @classmethod
    def from_env(cls) -> RapidApiSettings:
        mock_mode = is_mock_mode()
        api_key = os.environ.get(RAPIDAPI_KEY_ENV, "").strip()
        return cls(
            api_key=api_key,
            omdb_host=os.environ.get(OMDB_HOST_ENV, DEFAULT_OMDB_HOST).strip(),
            countries_host=os.environ.get(COUNTRIES_HOST_ENV, DEFAULT_COUNTRIES_HOST).strip(),
            streaming_host=os.environ.get(STREAMING_HOST_ENV, DEFAULT_STREAMING_HOST).strip(),
            mock_mode=mock_mode,
        )

    def require_live_credentials(self) -> None:
        if not self.mock_mode and not self.api_key:
            raise RapidApiNotConfiguredError(
                f"{RAPIDAPI_KEY_ENV} is not set. Add it to .env for live API calls."
            )

    @property
    def tools_ready(self) -> bool:
        return self.mock_mode or bool(self.api_key)


def _normalize_country_payload(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
    """Map heterogeneous RapidAPI / RestCountries payloads to a stable tool schema."""
    item: dict[str, Any]
    if isinstance(payload, list):
        item = payload[0] if payload else {}
    elif isinstance(payload, dict) and isinstance(payload.get("data"), list):
        data = payload["data"]
        item = data[0] if data else {}
    else:
        item = payload if isinstance(payload, dict) else {}

    name = item.get("name")
    if isinstance(name, dict):
        name = name.get("common") or name.get("official")

    capital = item.get("capital")
    if isinstance(capital, list):
        capital = capital[0] if capital else None

    region = item.get("region")
    if isinstance(region, dict):
        region = region.get("name")

    population = item.get("population")
    return {
        "name": name or item.get("country"),
        "capital": capital,
        "region": region,
        "population": population,
    }


def _normalize_title_search(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize IMDb autocomplete and mock payloads for Open WebUI."""
    suggestions = payload.get("results")
    if isinstance(suggestions, list) and suggestions and isinstance(suggestions[0], dict):
        if all(key in suggestions[0] for key in ("title",)) or len(suggestions[0]) > 1:
            return {"results": suggestions[:5]}

    raw = payload.get("d") or payload.get("data") or payload.get("results")
    if isinstance(raw, list):
        results = []
        for entry in raw[:5]:
            if isinstance(entry, dict):
                results.append(entry)
            elif isinstance(entry, str):
                results.append({"title": entry})
        return {"results": results}
    return {"results": [payload] if payload else []}


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
        self._http = httpx.Client(timeout=self._timeout, transport=self._transport)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> RapidApiClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _request(
        self,
        *,
        host: str,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self._settings.mock_mode:
            raise RuntimeError("Live RapidAPI request attempted while mock mode is enabled")
        self._settings.require_live_credentials()
        headers = {
            "X-RapidAPI-Key": self._settings.api_key,
            "X-RapidAPI-Host": host,
        }
        url = f"https://{host}{path}"
        try:
            response = self._http.request(method, url, headers=headers, params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RapidApiUpstreamError("External API request failed") from exc
        except httpx.HTTPError as exc:
            raise RapidApiUpstreamError("External API request failed") from exc

        payload = response.json()
        if isinstance(payload, dict):
            return payload
        return {"data": payload}

    def search_title(self, title: str) -> dict[str, Any]:
        """Search IMDb-style metadata for a Netflix title."""
        if self._settings.mock_mode:
            return {
                "results": [
                    {
                        "title": title,
                        "year": 2021,
                        "mock": True,
                    }
                ]
            }
        self._settings.require_live_credentials()
        raw = self._request(
            host=self._settings.omdb_host,
            method="GET",
            path="/auto-complete",
            params={"q": title.strip()},
        )
        return _normalize_title_search(raw)

    def country_info(self, country_name: str) -> dict[str, Any]:
        """Fetch country facts (capital, region, population)."""
        slug = country_name.strip().lower()
        if self._settings.mock_mode:
            fixture = _MOCK_COUNTRY_FIXTURES.get(slug)
            if fixture:
                return {**fixture, "mock": True}
            return {
                "name": country_name.strip().title(),
                "capital": "Unknown",
                "region": "Unknown",
                "population": None,
                "mock": True,
            }
        self._settings.require_live_credentials()
        encoded = quote(slug, safe="")
        raw = self._request(
            host=self._settings.countries_host,
            method="GET",
            path=f"/v3.1/name/{encoded}",
            params={"fields": "name,capital,region,population"},
        )
        normalized = _normalize_country_payload(raw)
        if not normalized.get("name"):
            raise RapidApiNotFoundError(f"No country found for: {country_name.strip()}")
        return normalized

    def streaming_status(self, title: str, country_code: str) -> dict[str, Any]:
        """Check streaming availability for a title in a country (ISO 3166-1 alpha-2)."""
        code = country_code.strip().upper()
        if not ISO_ALPHA2.match(code):
            raise ValueError("country_code must be ISO 3166-1 alpha-2 letters")

        if self._settings.mock_mode:
            return {
                "result": [
                    {
                        "title": title,
                        "country": code,
                        "streamingOptions": [{"service": "netflix", "mock": True}],
                    }
                ],
                "mock": True,
            }
        self._settings.require_live_credentials()
        return self._request(
            host=self._settings.streaming_host,
            method="GET",
            path="/shows/search/title",
            params={
                "title": title.strip(),
                "country": code,
                "output_language": "en",
                "show_type": "all",
            },
        )
