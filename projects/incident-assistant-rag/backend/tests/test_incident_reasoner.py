import pytest

from app.rag.generator import FakeIncidentAnswerGenerator
from app.reasoning.incident_reasoner import IncidentReasoner
from app.schemas.search_schema import SearchResult


class FakeRetriever:
    def __init__(self, results):
        self.results = results
    def retrieve(self, question: str, top_k: int = 5):
        return self.results[:top_k]


class BadJsonGenerator:
    def generate(self, prompt: str) -> str:
        return "not json"


def test_incident_reasoner_returns_structured_analysis():
    reasoner = IncidentReasoner(FakeRetriever([SearchResult(chunk_id="a", source_file="auth.md", chunk_index=0, text="Check auth-service logs", score=0.95)]), answer_generator=FakeIncidentAnswerGenerator(), score_threshold=0.25)
    response = reasoner.analyze("Many users cannot log in after deployment", "auth-service", "production")
    assert response.severity == "High"
    assert response.used_context is True


def test_incident_reasoner_bad_json_fallback():
    reasoner = IncidentReasoner(FakeRetriever([]), answer_generator=BadJsonGenerator(), score_threshold=0.25)
    response = reasoner.analyze("Unknown issue in the system", top_k=1)
    assert response.used_context is False
    assert "not contain enough" in response.likely_causes[0]


def test_incident_reasoner_rejects_empty_description():
    reasoner = IncidentReasoner(FakeRetriever([]), answer_generator=FakeIncidentAnswerGenerator())
    with pytest.raises(ValueError):
        reasoner.analyze(" ")


def test_incident_reasoner_rejects_zero_top_k():
    reasoner = IncidentReasoner(FakeRetriever([]), answer_generator=FakeIncidentAnswerGenerator())
    with pytest.raises(ValueError, match="top_k must be positive"):
        reasoner.analyze("This is ten plus chars incident", top_k=0)


def test_incident_reasoner_rejects_negative_top_k():
    reasoner = IncidentReasoner(FakeRetriever([]), answer_generator=FakeIncidentAnswerGenerator())
    with pytest.raises(ValueError, match="top_k must be positive"):
        reasoner.analyze("This is ten plus chars incident", top_k=-3)
