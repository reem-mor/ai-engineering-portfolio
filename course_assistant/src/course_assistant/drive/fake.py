"""In-memory Drive service for tests and local development.

Implements the two ``BaseDriveService`` primitives from a plain dict tree, so the
full resolution / recursion / classification path runs offline with no Google
credentials or network access.
"""

from __future__ import annotations

from course_assistant.drive.service import BaseDriveService, RawEntry


class FakeDriveService(BaseDriveService):
    """A :class:`BaseDriveService` backed by an in-memory folder tree.

    ``tree`` maps a folder ID to the list of its direct children. A folder ID
    that is absent (or maps to an empty list) models an empty folder — the
    "not uploaded yet" case.
    """

    def __init__(self, root_id: str, tree: dict[str, list[RawEntry]]) -> None:
        self._root = root_id
        self._tree = tree

    def _root_folder_id(self) -> str:
        return self._root

    def _list_children(self, folder_id: str) -> list[RawEntry]:
        return list(self._tree.get(folder_id, []))
