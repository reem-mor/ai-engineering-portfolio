"""The ``explain_homework_submission`` tool.

Returns the canonical submission procedure, sourced from the committed
``Homework_Submission_Procedure`` document — recipients, the exact subject
format, the body structure, attachments, and general guidelines. Bilingual.
"""

from __future__ import annotations

from course_assistant.homework.compose import EN_DASH, SUBJECT_PREFIX

_SUBJECT_TEMPLATE_EN = (
    f"{SUBJECT_PREFIX} {EN_DASH} <Your Full Name> {EN_DASH} <Course/Topic> {EN_DASH} <Date>"
)
_EXAMPLE_SUBJECT = (
    f"{SUBJECT_PREFIX} {EN_DASH} John Doe {EN_DASH} Python Basics {EN_DASH} 12/05/2026"
)


def _procedure_en(to: str, cc: str) -> str:
    return "\n".join(
        [
            "Homework is submitted by email, following this procedure:",
            "",
            f"1. Recipients — To: {to}; CC: {cc}.",
            "2. Subject line (exact format):",
            f"   {_SUBJECT_TEMPLATE_EN}",
            f"   Example: {_EXAMPLE_SUBJECT}",
            "3. Body — clear, professional English including:",
            "   • a concise explanation of the task,",
            "   • what you implemented or solved,",
            "   • key challenges (if any),",
            "   • what is attached.",
            "4. Attachments — all required files (code, documents, GitHub link, etc.).",
            "5. Guidelines — professional language, structured and concise, make sure every",
            "   file is included, and submit on time.",
            "",
            "I can draft this email for you and send it after you approve the preview.",
        ]
    )


def _procedure_he(to: str, cc: str) -> str:
    return "\n".join(
        [
            "הגשת שיעורי בית נעשית במייל, לפי הנוהל הבא:",
            "",
            f"1. נמענים — אל: {to}; עותק (CC): {cc}.",
            "2. שורת הנושא (פורמט מדויק):",
            f"   {_SUBJECT_TEMPLATE_EN}",
            f"   דוגמה: {_EXAMPLE_SUBJECT}",
            "3. גוף ההודעה — באנגלית מקצועית וברורה, וכולל:",
            "   • הסבר תמציתי על המשימה,",
            "   • מה מימשת או פתרת,",
            "   • אתגרים מרכזיים (אם היו),",
            "   • מה מצורף.",
            "4. קבצים מצורפים — כל הקבצים הנדרשים (קוד, מסמכים, קישור ל-GitHub וכו').",
            "5. הנחיות — שפה מקצועית, מובנה ותמציתי, לוודא שכל הקבצים מצורפים, ולהגיש בזמן.",
            "",
            "אני יכול לנסח עבורך את המייל ולשלוח אותו לאחר שתאשר/י את התצוגה המקדימה.",
        ]
    )


def explain_homework_submission(
    lang: str = "he",
    to_email: str | None = None,
    cc_email: str | None = None,
) -> str:
    """Explain how to submit homework. Uses real recipients when provided."""
    to = to_email or "Alex"
    cc = cc_email or "Sagy"
    if lang.lower().startswith("he"):
        return _procedure_he(to, cc)
    return _procedure_en(to, cc)
