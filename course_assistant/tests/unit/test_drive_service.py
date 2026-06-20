"""Tests for BaseDriveService logic, exercised through FakeDriveService."""

from __future__ import annotations

from course_assistant.drive.fake import FakeDriveService


def test_type_folders_resolve_by_hebrew_name(drive: FakeDriveService) -> None:
    # Resolution happens lazily; a successful materials lookup proves both
    # the root listing and the Hebrew-named type-folder match worked.
    assert drive.get_materials(2).found


def test_recordings_single_part(drive: FakeDriveService) -> None:
    recs = drive.get_recordings(1)
    assert recs.found and recs.uploaded
    assert [p.title for p in recs.parts] == ["part 1.mp4"]


def test_recordings_multipart_sorted(drive: FakeDriveService) -> None:
    recs = drive.get_recordings(3)
    assert [p.title for p in recs.parts] == ["part 1.mp4", "part 2.mp4", "intro.mp4"]


def test_recordings_empty_folder_is_not_uploaded(drive: FakeDriveService) -> None:
    recs = drive.get_recordings(7)
    assert recs.found is True
    assert recs.uploaded is False
    assert recs.parts == []


def test_recordings_missing_folder_not_found(drive: FakeDriveService) -> None:
    recs = drive.get_recordings(99)
    assert recs.found is False


def test_materials_flat_lesson_classified(drive: FakeDriveService) -> None:
    mats = drive.get_materials(2)
    assert mats.found
    assert sorted(f.title for f in mats.homework) == [
        "HW2 (2).docx",
        "Jupyter-intro-hw.docx",
        "Python-intro-hw.docx",
    ]
    assert [f.title for f in mats.slides] == ["lecture2.pptx (1).pdf"]
    assert mats.code == []


def test_materials_nested_hw_and_code_subfolders(drive: FakeDriveService) -> None:
    mats = drive.get_materials(10)
    assert [f.title for f in mats.homework] == ["פרויקט אמצע.docx"]
    assert [f.title for f in mats.code] == ["bedroc_agent.py"]


def test_materials_exercise_doc_is_homework(drive: FakeDriveService) -> None:
    mats = drive.get_materials(7)
    assert len(mats.homework) == 1
    assert "Exercise" in mats.homework[0].title


def test_materials_missing_lesson_not_found(drive: FakeDriveService) -> None:
    assert drive.get_materials(99).found is False
