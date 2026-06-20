"""Shared test fixtures."""

from __future__ import annotations

import pytest

from course_assistant.drive.fake import FakeDriveService
from tests.fixtures.drive_tree import build_tree


@pytest.fixture
def drive() -> FakeDriveService:
    """A FakeDriveService backed by the captured course-Drive snapshot."""
    root_id, tree = build_tree()
    return FakeDriveService(root_id, tree)
