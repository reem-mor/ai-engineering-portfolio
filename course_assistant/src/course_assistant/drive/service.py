"""Read-only Google Drive access to the course folder.

``BaseDriveService`` holds all the resolution / recursion / classification logic
and depends only on two primitives — ``_root_folder_id`` and ``_list_children``.
``GoogleDriveService`` implements those against the live (read-only) Drive API;
``FakeDriveService`` (see ``fake.py``) implements them from an in-memory tree, so
tests exercise the same enumeration code with no network calls.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any

from course_assistant.drive.classify import classify_kind, is_recording, sort_recording_parts
from course_assistant.drive.models import (
    DriveFile,
    LessonMaterials,
    LessonRecordings,
    MaterialKind,
)

if TYPE_CHECKING:
    from course_assistant.config import Settings

FOLDER_MIME = "application/vnd.google-apps.folder"

# Type-folder name hints (Hebrew first, English fallback for renames).
_RECORDINGS_HINTS = ("הקלטות", "recording")
_MATERIALS_HINTS = ("מצגות", "presentation", "slides", "material")

# How deep to recurse inside a lesson folder (lesson → HW/code subfolder → files).
_MAX_DEPTH = 3


@dataclass(frozen=True)
class RawEntry:
    """A raw Drive child entry (file or folder) before classification."""

    id: str
    title: str
    mime_type: str
    url: str

    @property
    def is_folder(self) -> bool:
        return self.mime_type == FOLDER_MIME


def _lesson_matches(title: str, lesson: int) -> bool:
    """True if a folder title refers to ``lesson`` (e.g. 'Lesson 7', 'שיעור 07', '7')."""
    numbers = re.findall(r"\d+", title)
    return any(int(n) == lesson for n in numbers)


class BaseDriveService(ABC):
    """Shared, transport-agnostic Drive logic."""

    @abstractmethod
    def _root_folder_id(self) -> str:
        """Return the course root folder ID."""

    @abstractmethod
    def _list_children(self, folder_id: str) -> list[RawEntry]:
        """List the immediate children of ``folder_id`` (files and folders)."""

    # -- type-folder resolution (cached per instance) -----------------------

    def _find_type_folder(self, hints: tuple[str, ...]) -> str | None:
        for child in self._list_children(self._root_folder_id()):
            if child.is_folder and any(h.lower() in child.title.lower() for h in hints):
                return child.id
        return None

    @cached_property
    def _recordings_root(self) -> str | None:
        return self._find_type_folder(_RECORDINGS_HINTS)

    @cached_property
    def _materials_root(self) -> str | None:
        return self._find_type_folder(_MATERIALS_HINTS)

    def _find_lesson_folder(self, type_folder_id: str | None, lesson: int) -> str | None:
        if type_folder_id is None:
            return None
        for child in self._list_children(type_folder_id):
            if child.is_folder and _lesson_matches(child.title, lesson):
                return child.id
        return None

    # -- recursive file collection ------------------------------------------

    def _collect_files(
        self, folder_id: str, parent_name: str, depth: int = 0
    ) -> list[tuple[RawEntry, str]]:
        """Return ``(file, parent_folder_name)`` pairs under ``folder_id``."""
        collected: list[tuple[RawEntry, str]] = []
        for child in self._list_children(folder_id):
            if child.is_folder:
                if depth + 1 < _MAX_DEPTH:
                    collected.extend(self._collect_files(child.id, child.title, depth + 1))
            else:
                collected.append((child, parent_name))
        return collected

    # -- public API ---------------------------------------------------------

    def get_recordings(self, lesson: int) -> LessonRecordings:
        """Recording parts for ``lesson`` (sorted; empty parts → not uploaded yet)."""
        folder = self._find_lesson_folder(self._recordings_root, lesson)
        if folder is None:
            return LessonRecordings(lesson=lesson, found=False)
        parts = [
            DriveFile(id=e.id, title=e.title, url=e.url, mime_type=e.mime_type)
            for e, _ in self._collect_files(folder, f"Lesson {lesson}")
            if is_recording(e.mime_type, e.title)
        ]
        return LessonRecordings(lesson=lesson, found=True, parts=sort_recording_parts(parts))

    def get_materials(self, lesson: int) -> LessonMaterials:
        """Slides / homework / code / other for ``lesson`` (recursively classified)."""
        folder = self._find_lesson_folder(self._materials_root, lesson)
        if folder is None:
            return LessonMaterials(lesson=lesson, found=False)

        buckets: dict[MaterialKind, list[DriveFile]] = {k: [] for k in MaterialKind}
        for entry, parent_name in self._collect_files(folder, f"Lesson {lesson}"):
            kind = classify_kind(entry.title, entry.mime_type, parent_name)
            buckets[kind].append(
                DriveFile(
                    id=entry.id,
                    title=entry.title,
                    url=entry.url,
                    mime_type=entry.mime_type,
                    kind=kind,
                )
            )
        return LessonMaterials(
            lesson=lesson,
            found=True,
            slides=buckets[MaterialKind.SLIDES],
            homework=buckets[MaterialKind.HOMEWORK],
            code=buckets[MaterialKind.CODE],
            other=buckets[MaterialKind.OTHER],
        )


class GoogleDriveService(BaseDriveService):
    """Live, read-only Drive access via OAuth credentials from settings.

    The Google client is built lazily so importing this module (and running the
    rest of the suite against the fake) needs no credentials or network.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._service: Any = None  # google api client, built on first use

    def _root_folder_id(self) -> str:
        folder_id = self._settings.drive_root_folder_id
        if not folder_id:
            raise RuntimeError("DRIVE_ROOT_FOLDER_ID is not configured.")
        return folder_id

    def _client(self) -> Any:  # pragma: no cover - exercised only with live credentials
        if self._service is not None:
            return self._service
        from google.oauth2.credentials import Credentials  # lazy imports
        from googleapiclient.discovery import build

        s = self._settings
        if not (
            s.google_oauth_client_id
            and s.google_oauth_client_secret
            and s.google_oauth_refresh_token
        ):
            raise RuntimeError("Google OAuth credentials are not fully configured.")
        creds = Credentials(  # type: ignore[no-untyped-call]
            token=None,
            refresh_token=s.google_oauth_refresh_token.get_secret_value(),
            client_id=s.google_oauth_client_id,
            client_secret=s.google_oauth_client_secret.get_secret_value(),
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return self._service

    def _list_children(self, folder_id: str) -> list[RawEntry]:  # pragma: no cover
        service = self._client()
        entries: list[RawEntry] = []
        page_token: str | None = None
        query = f"'{folder_id}' in parents and trashed = false"
        while True:
            resp = (
                service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, webViewLink)",
                    pageSize=200,
                    pageToken=page_token,
                )
                .execute()
            )
            for f in resp.get("files", []):
                entries.append(
                    RawEntry(
                        id=f["id"],
                        title=f.get("name", ""),
                        mime_type=f.get("mimeType", ""),
                        url=f.get("webViewLink", ""),
                    )
                )
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return entries
