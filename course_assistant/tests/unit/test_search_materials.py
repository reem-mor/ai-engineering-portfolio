"""Tests for the search_course_materials tool."""

from __future__ import annotations

from course_assistant.rag.embeddings import HashingEmbedder
from course_assistant.rag.stores import InMemoryVectorStore
from course_assistant.rag.vectorstore import Document
from course_assistant.tools.search_materials import search_course_materials


def _store() -> InMemoryVectorStore:
    store = InMemoryVectorStore(HashingEmbedder(dim=128))
    store.add(
        [
            Document(
                "2:0",
                "docker containers nginx and ec2 deployment exercise",
                "Ubuntu_EC2_Docker_Nginx_Student_Exercise.docx",
                {"lesson": "7", "url": "file/abc/view"},
            ),
            Document(
                "1:0",
                "python loops functions and variables intro",
                "Python-intro-hw.docx",
                {"lesson": "2", "url": "file/def/view"},
            ),
        ]
    )
    return store


def test_returns_snippet_with_source_and_lesson_and_link() -> None:
    out = search_course_materials(_store(), "how does docker and nginx work", k=1, lang="en")
    assert "docker containers" in out
    assert "Source: Ubuntu_EC2_Docker_Nginx_Student_Exercise.docx" in out
    assert "Lesson 7" in out
    assert "file/abc/view" in out


def test_no_results_message_when_store_empty() -> None:
    empty = InMemoryVectorStore(HashingEmbedder(dim=64))
    out = search_course_materials(empty, "anything", lang="en")
    assert "couldn't find" in out


def test_hebrew_no_results_message() -> None:
    empty = InMemoryVectorStore(HashingEmbedder(dim=64))
    out = search_course_materials(empty, "משהו", lang="he")
    assert "לא מצאתי" in out
