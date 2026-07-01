"""
title: HW07 Live Job Search
author: Re'em Mor
description: Calls the local hw07 tools server (JSearch via RapidAPI) for current job listings.
requirements: httpx, pydantic
version: 1.0.0
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel, Field


class Tools:
    """Open WebUI tool — proxies to host tools_server.py on port 5005."""

    class Valves(BaseModel):
        tools_server_url: str = Field(
            default="http://host.docker.internal:5005",
            description="URL of the hw07 tools server (must use host.docker.internal from Docker)",
        )

    def __init__(self) -> None:
        self.valves = self.Valves()

    async def search_live_jobs(
        self,
        role: str,
        location: str = "Israel",
        __event_emitter__=None,
    ) -> str:
        """
        Search current job openings via JSearch (live listings).

        :param role: Job title or keywords, e.g. "AI engineer" or "DevOps"
        :param location: Geographic filter, default Israel
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Searching live jobs for {role} in {location}...",
                        "done": False,
                    },
                }
            )

        url = f"{self.valves.tools_server_url.rstrip('/')}/jobs/search"
        payload = {"query": role, "location": location, "num_pages": 1}

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            return f"Tool server request failed: {exc}"

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Job search complete", "done": True},
                }
            )

        if not body.get("ok"):
            return f"Search failed: {body.get('error', 'unknown error')}"

        jobs = body.get("data") or []
        if not jobs:
            return f"No live listings found for **{role}** in **{location}**."

        lines = [f"**Live jobs for {role} in {location}** (source: {body.get('source', 'jsearch')})\n"]
        for idx, job in enumerate(jobs[:10], start=1):
            title = job.get("job_title") or "Unknown title"
            employer = job.get("employer_name") or "Unknown employer"
            city = job.get("job_city") or ""
            country = job.get("job_country") or location
            link = job.get("job_apply_link") or ""
            place = f"{city}, {country}".strip(", ")
            lines.append(f"{idx}. **{title}** — {employer} ({place})")
            if link:
                lines.append(f"   Apply: {link}")

        return "\n".join(lines)
