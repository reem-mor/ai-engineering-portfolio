"""Central intent dispatch for the deterministic router.

Routes a classified ``Intent`` to the matching feature handler. Keeps ``handlers.py`` free
of per-feature imports and avoids circular dependencies between feature modules.
"""

from __future__ import annotations

from app.bot.drive_handlers import reply_for_drive_intent
from app.bot.router import Intent, IntentName
from app.bot.schedule_handlers import reply_for_intent as reply_for_schedule_intent
from app.bot.summary_handlers import reply_for_summary_intent
from app.core.i18n import Language


async def dispatch_intent(intent: Intent, language: Language) -> str | None:
    """Return a reply for a routed intent, or None if no handler produced one."""
    if intent.name is IntentName.SCHEDULE:
        return reply_for_schedule_intent(intent, language)
    if intent.name is IntentName.SUMMARIZE:
        return await reply_for_summary_intent(intent, language)
    return await reply_for_drive_intent(intent, language)
