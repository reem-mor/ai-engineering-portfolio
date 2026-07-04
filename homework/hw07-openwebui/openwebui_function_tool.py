"""
title: Netflix Country Info
author: Re'em Mor
version: 1.1.0
description: Fetch live country details from the local Flask tool server.
"""

from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        base_url: str = Field(
            default="http://host.docker.internal:5005",
            description=(
                "Tool server base URL. Default fits Open WebUI in Docker with the "
                "Flask server on the host. Use http://localhost:5005 when Open WebUI "
                "runs directly on the host, or http://tools-server:5005 when both "
                "run in the same Docker Compose network."
            ),
        )

    def __init__(self):
        self.valves = self.Valves()

    def get_country_info(self, country: str) -> dict:
        """
        Get live country information (currency, ISO code, phone code, timezones).

        :param country: Country name, for example France, Japan, Brazil.
        :return: JSON response from the local server.
        """
        base_url = self.valves.base_url.rstrip("/")
        url = f"{base_url}/country/{quote(country, safe='')}"

        try:
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}",
                "country": country,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "country": country,
            }
