"""Dependencies injected into the agent's tools."""

from __future__ import annotations

from dataclasses import dataclass

from course_assistant.config import Settings
from course_assistant.drive.service import BaseDriveService
from course_assistant.rag.vectorstore import VectorStore


@dataclass
class AgentDeps:
    """Services + conversation language the agent tools render against."""

    drive: BaseDriveService
    store: VectorStore
    settings: Settings
    lang: str = "he"
