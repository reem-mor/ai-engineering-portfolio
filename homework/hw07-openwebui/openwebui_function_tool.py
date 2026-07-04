"""
title: Netflix Country Info
author: Homework
version: 1.0.0
description: Fetch live country details from the local Flask tool server.
"""

from urllib.parse import quote

import httpx


class Tools:
    def get_country_info(self, country: str) -> dict:
        """
        Get live country information from the local Flask server.

        :param country: Country name, for example France, Japan, Brazil.
        :return: JSON response from the local server.
        """
        url = f"http://localhost:5005/country/{quote(country, safe='')}"

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
