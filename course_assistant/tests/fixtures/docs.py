"""Helpers to build small real document bytes for extraction/ingestion tests."""

from __future__ import annotations

import io


def make_docx(paragraphs: list[str]) -> bytes:
    """Return the bytes of a minimal .docx containing ``paragraphs``."""
    from docx import Document

    document = Document()
    for text in paragraphs:
        document.add_paragraph(text)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()
