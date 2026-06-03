"""Stdio MCP server exposing course demo tools for Cursor and MCP Inspector."""

from __future__ import annotations

import random

from mcp.server.fastmcp import FastMCP
from datetime import datetime, timezone
mcp = FastMCP(

    "course-tools",
    instructions="Demo MCP server for Lecture 08. Tools: get_weather, get_joke.",
)

WEATHER_BY_CITY: dict[str, str] = {
    "Tel Aviv": "27°C and sunny",
    "London": "15°C and rainy",
    "New York": "22°C and cloudy",
}

JOKES: tuple[str, ...] = (
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "A SQL query walks into a bar and asks: 'Can I join you?'",
    "There are only 10 kinds of people: those who understand binary and those who don't.",
)


@mcp.tool()
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    normalized = city.strip()
    if not normalized:
        return "City name is required."
    for known_city, forecast in WEATHER_BY_CITY.items():
        if known_city.lower() == normalized.lower():
            return forecast
    return f"No weather data for {normalized}"


@mcp.tool()
def get_joke() -> str:
    """Tell a random programming joke."""
    return random.choice(JOKES)


if __name__ == "__main__":
    mcp.run()

@mcp.tool()
def get_current_time() -> str:
    """Return the current UTC time."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
