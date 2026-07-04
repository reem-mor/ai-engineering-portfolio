import os
from pathlib import Path

from flask import Flask, jsonify
from dotenv import load_dotenv
import httpx

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "country-state-city-search-rest-api.p.rapidapi.com"
_PLACEHOLDER_KEYS = {"", "your_rapidapi_key_here"}


def _api_key_configured() -> bool:
    return bool(RAPIDAPI_KEY and RAPIDAPI_KEY.strip() not in _PLACEHOLDER_KEYS)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "server": "tools_server",
        "port": 5005
    })


@app.get("/country/<country_name>")
def get_country_info(country_name):
    if not _api_key_configured():
        return jsonify({
            "success": False,
            "error": "Missing RAPIDAPI_KEY in environment"
        }), 500

    url = "https://country-state-city-search-rest-api.p.rapidapi.com/allcountries"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return jsonify({
                "success": False,
                "error": f"External API returned status {response.status_code}",
                "message": response.text
            }), response.status_code

        countries = response.json()

        match = None
        for item in countries:
            name = item.get("name", "").lower()
            if name == country_name.lower():
                match = item
                break

        if not match:
            return jsonify({
                "success": False,
                "error": f"Country '{country_name}' not found"
            }), 404

        return jsonify({
            "success": True,
            "country": country_name,
            "data": match
        }), 200

    except httpx.TimeoutException:
        return jsonify({
            "success": False,
            "error": "Request timeout while calling external API"
        }), 503

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
