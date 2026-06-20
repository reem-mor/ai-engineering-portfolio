"""Unit tests for the pure Drive classification helpers."""

from __future__ import annotations

import pytest

from course_assistant.drive.classify import (
    classify_kind,
    is_recording,
    recording_part_index,
    sort_recording_parts,
)
from course_assistant.drive.models import DriveFile, MaterialKind

_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_PDF = "application/pdf"


@pytest.mark.parametrize(
    ("title", "mime", "folder", "expected"),
    [
        ("Python-intro-hw.docx", _DOCX, None, MaterialKind.HOMEWORK),
        ("HW2 (2).docx", _DOCX, None, MaterialKind.HOMEWORK),
        ("Ubuntu_EC2_Docker_Nginx_Student_Exercise.docx", _DOCX, None, MaterialKind.HOMEWORK),
        ("lecture2.pptx (1).pdf", _PDF, None, MaterialKind.SLIDES),
        ("bedroc_agent.py", "text/x-python", None, MaterialKind.CODE),
        ("notes.txt", "text/plain", None, MaterialKind.OTHER),
    ],
)
def test_classify_by_name_and_extension(
    title: str, mime: str, folder: str | None, expected: MaterialKind
) -> None:
    assert classify_kind(title, mime, folder) is expected


def test_parent_folder_overrides_filename() -> None:
    """A code-extension file inside an HW/ folder is homework; a doc in code/ is code."""
    assert classify_kind("solution.py", "text/x-python", "HW") is MaterialKind.HOMEWORK
    assert classify_kind("פרויקט אמצע.docx", _DOCX, "HW") is MaterialKind.HOMEWORK
    assert classify_kind("README.docx", _DOCX, "code") is MaterialKind.CODE


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("part 1.mp4", 1),
        ("part 2.mp4", 2),
        ("part_3.mp4", 3),
        ("חלק 4.mp4", 4),
        ("intro.mp4", None),
    ],
)
def test_recording_part_index(title: str, expected: int | None) -> None:
    assert recording_part_index(title) == expected


def test_is_recording() -> None:
    assert is_recording("video/mp4", "part 1.mp4")
    assert is_recording("", "lecture.mov")  # extension fallback
    assert not is_recording(_DOCX, "homework.docx")


def test_sort_recording_parts_handles_order_gaps_and_unlabeled() -> None:
    files = [
        DriveFile("c", "part 2.mp4", "u", "video/mp4"),
        DriveFile("a", "intro.mp4", "u", "video/mp4"),
        DriveFile("b", "part 1.mp4", "u", "video/mp4"),
    ]
    ordered = [f.title for f in sort_recording_parts(files)]
    assert ordered == ["part 1.mp4", "part 2.mp4", "intro.mp4"]
