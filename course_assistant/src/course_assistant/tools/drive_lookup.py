"""The ``drive_lookup`` tool: fetch lesson recordings, slides, homework, or code.

Returns a bilingual (HE/EN) text answer with shareable Drive links, and clear
fallbacks distinguishing "no folder for this lesson yet" from "folder exists but
nothing uploaded yet". Never fabricates links — it reports only what Drive shows.
"""

from __future__ import annotations

from enum import StrEnum

from course_assistant.drive.models import DriveFile, LessonMaterials, MaterialKind
from course_assistant.drive.service import BaseDriveService


class DriveCategory(StrEnum):
    """What the student asked for."""

    RECORDINGS = "recordings"
    SLIDES = "slides"
    HOMEWORK = "homework"
    CODE = "code"
    ALL = "all"


_HEADINGS = {
    "he": {
        DriveCategory.RECORDINGS: "הקלטות",
        DriveCategory.SLIDES: "מצגות",
        DriveCategory.HOMEWORK: "שיעורי בית",
        DriveCategory.CODE: "קוד לדוגמה",
    },
    "en": {
        DriveCategory.RECORDINGS: "Recordings",
        DriveCategory.SLIDES: "Slides",
        DriveCategory.HOMEWORK: "Homework",
        DriveCategory.CODE: "Code examples",
    },
}

_MSG = {
    "he": {
        "no_folder": "עדיין אין תיקייה לשיעור {lesson}.",
        "not_uploaded": "ההקלטות לשיעור {lesson} עדיין לא הועלו.",
        "none_of_kind": "לא נמצאו {kind} לשיעור {lesson}.",
        "part": "חלק {i}",
    },
    "en": {
        "no_folder": "There's no folder for lesson {lesson} yet.",
        "not_uploaded": "The recordings for lesson {lesson} haven't been uploaded yet.",
        "none_of_kind": "No {kind} found for lesson {lesson}.",
        "part": "Part {i}",
    },
}

_MATERIAL_CATEGORIES = (DriveCategory.SLIDES, DriveCategory.HOMEWORK, DriveCategory.CODE)
_KIND_BY_CATEGORY = {
    DriveCategory.SLIDES: MaterialKind.SLIDES,
    DriveCategory.HOMEWORK: MaterialKind.HOMEWORK,
    DriveCategory.CODE: MaterialKind.CODE,
}


def _lang(lang: str) -> str:
    return "he" if lang.lower().startswith("he") else "en"


def _file_line(file: DriveFile) -> str:
    return f"• {file.title} — {file.url}"


def _render_recordings(service: BaseDriveService, lesson: int, lang: str) -> str:
    recs = service.get_recordings(lesson)
    head = _HEADINGS[lang][DriveCategory.RECORDINGS]
    if not recs.found:
        return f"{head}: " + _MSG[lang]["no_folder"].format(lesson=lesson)
    if not recs.parts:
        return f"{head}: " + _MSG[lang]["not_uploaded"].format(lesson=lesson)
    lines = [f"{head} ({len(recs.parts)}):"]
    for i, part in enumerate(recs.parts, start=1):
        label = _MSG[lang]["part"].format(i=i)
        lines.append(f"• {label}: {part.title} — {part.url}")
    return "\n".join(lines)


def _render_material_category(
    materials: LessonMaterials, category: DriveCategory, lang: str
) -> str:
    head = _HEADINGS[lang][category]
    if not materials.found:
        return f"{head}: " + _MSG[lang]["no_folder"].format(lesson=materials.lesson)
    files = materials.by_kind(_KIND_BY_CATEGORY[category])
    if not files:
        return f"{head}: " + _MSG[lang]["none_of_kind"].format(
            kind=head, lesson=materials.lesson
        )
    return "\n".join([f"{head} ({len(files)}):", *(_file_line(f) for f in files)])


def drive_lookup(
    service: BaseDriveService,
    lesson: int,
    category: DriveCategory = DriveCategory.ALL,
    lang: str = "he",
) -> str:
    """Look up Drive materials for ``lesson`` and render a bilingual answer.

    Args:
        service: A read-only Drive service (live or fake).
        lesson: Lesson number (1-based).
        category: Which artifact type to return, or ``ALL`` for everything.
        lang: ``"he"`` or ``"en"`` (anything starting with ``he`` → Hebrew).
    """
    lang = _lang(lang)

    if category is DriveCategory.RECORDINGS:
        return _render_recordings(service, lesson, lang)

    if category in _MATERIAL_CATEGORIES:
        materials = service.get_materials(lesson)
        return _render_material_category(materials, category, lang)

    # ALL: recordings + every materials category.
    materials = service.get_materials(lesson)
    sections = [_render_recordings(service, lesson, lang)]
    sections += [
        _render_material_category(materials, cat, lang) for cat in _MATERIAL_CATEGORIES
    ]
    return "\n\n".join(sections)
