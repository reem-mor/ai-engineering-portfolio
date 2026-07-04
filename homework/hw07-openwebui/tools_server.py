import os
from pathlib import Path
import unicodedata

from dotenv import load_dotenv
from flask import Flask, jsonify
import httpx

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
# Host header MUST match the API host in the request URL below, or RapidAPI 401s.
RAPIDAPI_HOST = "country-state-city-search-rest-api.p.rapidapi.com"
_PLACEHOLDER_KEYS = {"", "your_rapidapi_key_here"}


def _api_key_configured() -> bool:
    return bool(RAPIDAPI_KEY and RAPIDAPI_KEY.strip().lower() not in _PLACEHOLDER_KEYS)


def _normalize_country_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(char for char in normalized if not unicodedata.combining(char)).lower()


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "server": "tools_server",
        "port": 5005,
    })


@app.get("/country/<country_name>")
def get_country_info(country_name):
    if not _api_key_configured():
        return jsonify({
            "success": False,
            "error": "Missing RAPIDAPI_KEY in environment",
        }), 500

    url = "https://country-state-city-search-rest-api.p.rapidapi.com/allcountries"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            app.logger.warning("External API returned status %s", response.status_code)
            return jsonify({
                "success": False,
                "error": f"External API returned status {response.status_code}",
            }), response.status_code

        countries = response.json()

        match = None
        requested_name = _normalize_country_name(country_name)
        for item in countries:
            api_name = _normalize_country_name(item.get("name", ""))
            if api_name == requested_name or requested_name in api_name:
                match = item
                break

        if not match:
            return jsonify({
                "success": False,
                "error": f"Country '{country_name}' not found",
            }), 404

        return jsonify({
            "success": True,
            "country": country_name,
            "data": match,
        }), 200

    except httpx.TimeoutException:
        return jsonify({
            "success": False,
            "error": "Request timeout while calling external API",
        }), 503

    except Exception:
        app.logger.exception("Unexpected error while calling external API")
        return jsonify({
            "success": False,
            "error": "Unexpected error while calling external API",
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=os.getenv("FLASK_DEBUG") == "1")
