"""Data models for Drive retrieval.

These mirror the real course-Drive layout discovered during Phase 2:

```
root  (עוז ורוח מחזור 1)
├── Homework Submission Procedure.docx
├── הקלטות  (recordings type-folder)
│   └── Lesson N/ → "part 1.mp4", "part 2.mp4", …   (may be empty)
└── מצגות   (materials type-folder)
    └── Lesson N/ → slides (lectureN.pdf), homework (*-hw.docx),
                    optional HW/ and code/ subfolders
```
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class MaterialKind(StrEnum):
    """How a non-recording file is classified within a lesson's materials."""

    SLIDES = "slides"
    HOMEWORK = "homework"
    CODE = "code"
    OTHER = "other"


@dataclass(frozen=True)
class DriveFile:
    """A single Drive file with a shareable view link (never downloaded)."""

    id: str
    title: str
    url: str
    mime_type: str
    kind: MaterialKind = MaterialKind.OTHER


@dataclass(frozen=True)
class LessonRecordings:
    """Recordings for one lesson.

    ``found`` distinguishes "no recordings folder for this lesson" from
    "folder exists but is empty" (``found`` True, ``parts`` empty → not uploaded yet).
    """

    lesson: int
    found: bool
    parts: list[DriveFile] = field(default_factory=list)

    @property
    def uploaded(self) -> bool:
        return bool(self.parts)


@dataclass(frozen=True)
class LessonMaterials:
    """Slides / homework / code / other for one lesson, classified recursively.

    ``found`` is whether the lesson folder exists at all under the materials
    type-folder; each category list is empty when nothing of that kind is present.
    """

    lesson: int
    found: bool
    slides: list[DriveFile] = field(default_factory=list)
    homework: list[DriveFile] = field(default_factory=list)
    code: list[DriveFile] = field(default_factory=list)
    other: list[DriveFile] = field(default_factory=list)

    def by_kind(self, kind: MaterialKind) -> list[DriveFile]:
        return {
            MaterialKind.SLIDES: self.slides,
            MaterialKind.HOMEWORK: self.homework,
            MaterialKind.CODE: self.code,
            MaterialKind.OTHER: self.other,
        }[kind]
