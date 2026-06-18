"""Minimal i18n scaffolding (he/en).

Phase 0 only needs onboarding and echo strings; later phases extend the catalog.
User-facing strings live here, never inline in handlers. Hebrew is the default when
language detection is ambiguous, matching the cohort.
"""

from __future__ import annotations

from typing import Literal

Language = Literal["he", "en"]

DEFAULT_LANGUAGE: Language = "he"

# A heuristic good enough for Phase 0: any Hebrew code-point => Hebrew.
_HEBREW_RANGE = range(0x0590, 0x05FF + 1)

_CATALOG: dict[str, dict[Language, str]] = {
    "start": {
        "he": (
            "שלום! אני העוזר הרשמי של קורס \"עוז ורוח\". 🤖\n\n"
            "בקרוב אוכל לעזור עם: לוח הזמנים והשיעור הבא, סיכומי שיעורים, "
            "חומרי לימוד מומלצים, שיעורי בית והגשתם, והקלטות.\n\n"
            "כרגע אני בהרצה ראשונית (שלב 0) — שלחו הודעה ואחזיר אותה כהד."
        ),
        "en": (
            "Hi! I'm the official assistant for the \"Oz VeRuach\" course. 🤖\n\n"
            "Soon I'll help with: schedule and next lesson, lesson summaries, "
            "recommended materials, homework and submissions, and recordings.\n\n"
            "Right now I'm in early bring-up (Phase 0) — send a message and I'll echo it."
        ),
    },
    "echo_prefix": {
        "he": "קיבלתי",
        "en": "You said",
    },
    "empty_message": {
        "he": "לא קיבלתי טקסט לטיפול.",
        "en": "I didn't receive any text to handle.",
    },
    "myid": {
        "he": "מזהה ה-Telegram המספרי שלך הוא: {id}\nתפקיד: {role}",
        "en": "Your numeric Telegram ID is: {id}\nRole: {role}",
    },
    "role_owner": {"he": "בעלים (מנהל-על)", "en": "owner (superadmin)"},
    "role_admin": {"he": "מנהל", "en": "admin"},
    "role_student": {"he": "סטודנט", "en": "student"},
    # --- Schedule (Phase 1) ---------------------------------------------------
    "sched_next_header": {"he": "השיעור הבא:", "en": "Next lesson:"},
    "sched_week_header": {
        "he": "השבוע ({start}–{end}):",
        "en": "This week ({start}–{end}):",
    },
    "sched_week_empty": {
        "he": "אין שיעורים מתוכננים השבוע.",
        "en": "No sessions are scheduled this week.",
    },
    "sched_full_header": {"he": "מערכת השעות המלאה:", "en": "Full course schedule:"},
    "sched_week_group": {"he": "שבוע {n}", "en": "Week {n}"},
    "sched_course_finished": {
        "he": "הקורס הסתיים — כל השיעורים כבר התקיימו.",
        "en": "The course has finished — all sessions are in the past.",
    },
    "sched_holiday_today": {
        "he": "לתשומת לבכם: היום חג/חופשה, אין שיעור רגיל.",
        "en": "Heads up: today is a holiday/break, no regular class.",
    },
    "sched_nontechnical_note": {
        "he": "הערה: מפגש שאינו טכני — לרוב אין חומרי קורס/הקלטה.",
        "en": "Note: non-technical session — usually no course materials/recording.",
    },
    "label_instructor": {"he": "מרצה", "en": "Instructor"},
    "label_type": {"he": "סוג", "en": "Type"},
    "type_technical": {"he": "טכני", "en": "technical"},
    "type_workshop": {"he": "סדנה", "en": "workshop"},
    "type_milestone": {"he": "אבן דרך", "en": "milestone"},
    "type_holiday": {"he": "חג/חופשה", "en": "holiday"},
    "day_Sun": {"he": "יום ראשון", "en": "Sunday"},
    "day_Mon": {"he": "יום שני", "en": "Monday"},
    "day_Tue": {"he": "יום שלישי", "en": "Tuesday"},
    "day_Wed": {"he": "יום רביעי", "en": "Wednesday"},
    "day_Thu": {"he": "יום חמישי", "en": "Thursday"},
    "day_Fri": {"he": "יום שישי", "en": "Friday"},
    "day_Sat": {"he": "יום שבת", "en": "Saturday"},
    # --- Drive / recordings / homework (Phase 2) ------------------------------
    "drive_not_configured": {
        "he": "הגישה ל-Drive עדיין לא הוגדרה. פנו למפעיל הבוט.",
        "en": "Drive access isn't configured yet. Contact the bot operator.",
    },
    "rec_header": {"he": "הקלטה — {label}:", "en": "Recording — {label}:"},
    "rec_part_line": {"he": "חלק {n}: {url}", "en": "Part {n}: {url}"},
    "rec_not_linked": {
        "he": "ההקלטה של שיעור זה עדיין לא קושרה.",
        "en": "The recording for this lesson isn't linked yet.",
    },
    "rec_not_uploaded": {
        "he": "ההקלטה עדיין לא הועלתה.",
        "en": "The recording hasn't been uploaded yet.",
    },
    "rec_gap_note": {
        "he": "הערה: ייתכן שחלק מהחלקים חסרים.",
        "en": "Note: some parts may be missing.",
    },
    "rec_last_none": {
        "he": "לא נמצאה הקלטה אחרונה מקושרת עדיין.",
        "en": "No linked recent recording was found yet.",
    },
    "rec_all_header": {"he": "הקלטות זמינות:", "en": "Available recordings:"},
    "rec_all_item_empty": {"he": "{label}: טרם הועלתה", "en": "{label}: not uploaded yet"},
    "rec_all_item_count": {
        "he": "{label}: {n} חלקים",
        "en": "{label}: {n} part(s)",
    },
    "hw_header": {"he": "המטלה האחרונה ({lesson}):", "en": "Latest homework ({lesson}):"},
    "hw_item": {"he": "• {title}: {url}", "en": "• {title}: {url}"},
    "hw_multiple_note": {
        "he": "נמצאו כמה מטלות — בחרו אחת:",
        "en": "Multiple homework docs found — pick one:",
    },
    "hw_none": {
        "he": "לא נמצאה מטלה זמינה עדיין.",
        "en": "No homework was found yet.",
    },
    # --- Admin / lesson_map (Phase 2) -----------------------------------------
    "admin_refused": {
        "he": "הפקודה הזו מיועדת למנהלים בלבד.",
        "en": "This command is for admins only.",
    },
    "owner_refused": {
        "he": "הפקודה הזו מיועדת לבעלים בלבד.",
        "en": "This command is for the owner only.",
    },
    "map_header": {"he": "מיפוי השיעורים (lesson_map):", "en": "Lesson map:"},
    "map_recordings_label": {
        "he": "תיקיות הקלטה של אלכס:",
        "en": "Alex's recording folders:",
    },
    "map_links_label": {"he": "קישורים מאומתים:", "en": "Confirmed session links:"},
    "map_no_links": {"he": "אין עדיין קישורים מאומתים.", "en": "No confirmed links yet."},
    "map_suggest_header": {
        "he": "הצעות מיפוי (לא הוחלו — אשרו עם /map link):",
        "en": "Mapping suggestions (not applied — confirm with /map link):",
    },
    "map_suggest_none": {"he": "אין הצעות חדשות.", "en": "No new suggestions."},
    "map_link_saved": {
        "he": "נשמר: {date} → הקלטה {rec}, מצגת {pres}",
        "en": "Saved: {date} -> recording {rec}, presentation {pres}",
    },
    "map_usage": {
        "he": (
            "שימוש:\n/map — הצגת המיפוי\n/map suggest — הצעות\n"
            "/map link <YYYY-MM-DD> rec=<מספר> pres=<מספר>"
        ),
        "en": (
            "Usage:\n/map — show the map\n/map suggest — proposals\n"
            "/map link <YYYY-MM-DD> rec=<n> pres=<n>"
        ),
    },
    # --- Summaries (Phase 3) --------------------------------------------------
    "sum_header": {"he": "סיכום — {lesson}:", "en": "Summary — {lesson}:"},
    "sum_no_materials": {
        "he": "אין עדיין חומרים מקושרים לשיעור הזה לסיכום.",
        "en": "No materials are linked yet for this lesson to summarize.",
    },
    "sum_llm_unavailable": {
        "he": "שירות הסיכום אינו זמין כרגע (לא הוגדר ספק מודל).",
        "en": "Summaries aren't available right now (no model provider configured).",
    },
    "sum_working": {
        "he": "עובד על סיכום מההקלטה — זה עשוי לקחת רגע…",
        "en": "Working on a summary from the recording — this may take a moment…",
    },
}


def detect_language(text: str | None) -> Language:
    """Detect message language from its characters.

    Returns ``he`` if any Hebrew character is present, otherwise ``en``. Falls back to
    the default language for empty input.
    """
    if not text:
        return DEFAULT_LANGUAGE
    if any(ord(ch) in _HEBREW_RANGE for ch in text):
        return "he"
    return "en"


def t(key: str, language: Language) -> str:
    """Translate a catalog key into the requested language.

    Falls back to the default language, then to the key itself, so a missing string is
    visible but never crashes a handler.
    """
    entry = _CATALOG.get(key)
    if entry is None:
        return key
    return entry.get(language) or entry.get(DEFAULT_LANGUAGE) or key
