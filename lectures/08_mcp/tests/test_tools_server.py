"""Unit tests for MCP tool logic (no stdio transport)."""

from server.tools_server import JOKES, WEATHER_BY_CITY, get_joke, get_weather


def test_get_weather_known_city() -> None:
    assert get_weather("Tel Aviv") == WEATHER_BY_CITY["Tel Aviv"]


def test_get_weather_case_insensitive() -> None:
    assert get_weather("london") == WEATHER_BY_CITY["London"]


def test_get_weather_unknown_city() -> None:
    assert "No weather data" in get_weather("Paris")


def test_get_weather_empty_city() -> None:
    assert "required" in get_weather("  ")


def test_get_joke_returns_known_joke() -> None:
    assert get_joke() in JOKES
