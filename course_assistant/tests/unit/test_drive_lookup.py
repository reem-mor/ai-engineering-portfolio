"""Tests for the drive_lookup tool rendering and fallbacks."""

from __future__ import annotations

from course_assistant.drive.fake import FakeDriveService
from course_assistant.tools.drive_lookup import DriveCategory, drive_lookup


def test_recordings_lists_parts_with_links_en(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 1, DriveCategory.RECORDINGS, lang="en")
    assert "Recordings (1)" in out
    assert "Part 1" in out
    assert "file/1szPuDb5DzwYg7jPcud49XjRWU3zEOGix/view" in out


def test_recordings_empty_folder_message(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 7, DriveCategory.RECORDINGS, lang="en")
    assert "haven't been uploaded yet" in out


def test_recordings_missing_folder_message(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 99, DriveCategory.RECORDINGS, lang="en")
    assert "no folder for lesson 99 yet" in out


def test_homework_lists_three_files(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 2, DriveCategory.HOMEWORK, lang="en")
    assert "Homework (3)" in out
    assert "Python-intro-hw.docx" in out


def test_category_absent_reports_none_of_kind(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 2, DriveCategory.CODE, lang="en")
    assert "No Code examples found for lesson 2" in out


def test_all_combines_sections(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 10, DriveCategory.ALL, lang="en")
    # Lesson 10 has no recordings folder, but has homework + code materials.
    assert "no folder for lesson 10 yet" in out  # recordings section
    assert "פרויקט אמצע.docx" in out  # homework
    assert "bedroc_agent.py" in out  # code


def test_hebrew_rendering(drive: FakeDriveService) -> None:
    out = drive_lookup(drive, 1, DriveCategory.RECORDINGS, lang="he")
    assert "הקלטות" in out
    assert "חלק 1" in out
