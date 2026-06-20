"""Pure classification helpers for Drive files.

No I/O here — these functions take already-listed file metadata and decide what
kind of material each file is, and how to order multi-part recordings. Keeping
them pure makes the tricky heuristics (mixed flat/nested folders, tolerant
part-sorting) cheap to unit-test.
"""

from __future__ import annotations

import re

from course_assistant.drive.models import DriveFile, MaterialKind

# Folder-name hints (the materials folder uses nested HW/ and code/ subfolders
# in newer lessons). Hebrew + English so the heuristic survives renames.
_HOMEWORK_FOLDER_HINTS = ("hw", "homework", "פרויקט", "project")
_CODE_FOLDER_HINTS = ("code", "קוד")

# Filename hints, used when the parent folder gives no signal (flat lessons).
_HOMEWORK_NAME_RE = re.compile(
    r"(?:\bhw\d*\b|homework|exercise|תרגיל|פרויקט|project)", re.IGNORECASE
)
_SLIDES_NAME_RE = re.compile(r"(?:lecture|slides|presentation|מצגת)", re.IGNORECASE)

_CODE_EXTENSIONS = frozenset(
    {"py", "ipynb", "js", "ts", "java", "go", "rb", "sql", "sh", "json", "yaml", "yml"}
)
_SLIDE_EXTENSIONS = frozenset({"pdf", "pptx", "ppt", "key"})

# "part 1", "part 3.mp4", "part_2", "חלק 2" → captures the index.
_PART_RE = re.compile(r"(?:part|חלק)\s*_?\s*(\d+)", re.IGNORECASE)


def _extension(title: str) -> str:
    _, _, ext = title.rpartition(".")
    return ext.lower() if ext and ext != title else ""


def is_recording(mime_type: str, title: str) -> bool:
    """True if the file is a lecture recording (a video)."""
    return mime_type.startswith("video/") or _extension(title) in {"mp4", "mov", "mkv", "webm"}


def recording_part_index(title: str) -> int | None:
    """Return the part number from a recording filename, or ``None`` if unlabeled."""
    match = _PART_RE.search(title)
    return int(match.group(1)) if match else None


def sort_recording_parts(files: list[DriveFile]) -> list[DriveFile]:
    """Order recording parts tolerantly.

    Numbered parts come first in ascending order (handling gaps like part 1 then
    part 3); unlabeled files follow, ordered by title. Stable for equal keys.
    """

    def key(f: DriveFile) -> tuple[int, int, str]:
        idx = recording_part_index(f.title)
        # (has-no-index flag, index, title) — labeled parts sort ahead of unlabeled.
        return (1, 0, f.title.lower()) if idx is None else (0, idx, f.title.lower())

    return sorted(files, key=key)


def classify_kind(title: str, mime_type: str, parent_folder_name: str | None) -> MaterialKind:
    """Classify a materials file as slides / homework / code / other.

    The parent folder name wins when it is a clear ``HW``/``code`` bucket
    (newer lessons); otherwise fall back to filename and extension heuristics
    (flat lessons).
    """
    folder = (parent_folder_name or "").strip().lower()
    if folder:
        if any(hint in folder for hint in _HOMEWORK_FOLDER_HINTS):
            return MaterialKind.HOMEWORK
        if any(hint in folder for hint in _CODE_FOLDER_HINTS):
            return MaterialKind.CODE

    ext = _extension(title)
    if _HOMEWORK_NAME_RE.search(title):
        return MaterialKind.HOMEWORK
    if ext in _CODE_EXTENSIONS:
        return MaterialKind.CODE
    if ext in _SLIDE_EXTENSIONS or _SLIDES_NAME_RE.search(title):
        return MaterialKind.SLIDES
    return MaterialKind.OTHER
