"""The ``search_course_materials`` tool: RAG retrieval over ingested materials.

Returns the most relevant snippets from the course materials, each with a
pointer to its source (file title, lesson, and Drive link). If nothing relevant
is found, it says so plainly rather than guessing.
"""

from __future__ import annotations

from course_assistant.rag.vectorstore import SearchResult, VectorStore

_SNIPPET_CHARS = 320

_MSG = {
    "he": {
        "none": "לא מצאתי חומר רלוונטי בחומרי הקורס לשאלה הזו.",
        "header": "מצאתי את הקטעים הבאים בחומרי הקורס:",
        "source": "מקור",
        "lesson": "שיעור",
    },
    "en": {
        "none": "I couldn't find anything relevant in the course materials for that.",
        "header": "Here's what I found in the course materials:",
        "source": "Source",
        "lesson": "Lesson",
    },
}


def _lang(lang: str) -> str:
    return "he" if lang.lower().startswith("he") else "en"


def _snippet(text: str) -> str:
    snippet = " ".join(text.split())
    return snippet if len(snippet) <= _SNIPPET_CHARS else snippet[:_SNIPPET_CHARS].rstrip() + "…"


def _format_result(result: SearchResult, lang: str) -> str:
    doc = result.document
    parts = [f"“{_snippet(doc.text)}”"]
    citation = f"{_MSG[lang]['source']}: {doc.source}"
    lesson = doc.metadata.get("lesson")
    if lesson:
        citation += f" ({_MSG[lang]['lesson']} {lesson})"
    url = doc.metadata.get("url")
    if url:
        citation += f" — {url}"
    parts.append(citation)
    return "\n".join(parts)


def search_course_materials(
    store: VectorStore,
    query: str,
    k: int = 4,
    lang: str = "he",
) -> str:
    """Retrieve relevant course-material snippets for ``query``, with sources."""
    lang = _lang(lang)
    results = store.search(query, k=k)
    if not results:
        return _MSG[lang]["none"]
    blocks = [_MSG[lang]["header"], ""]
    blocks.extend(_format_result(r, lang) for r in results)
    return "\n\n".join(blocks)
