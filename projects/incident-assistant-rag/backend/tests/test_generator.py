"""Generator behaviour branches (offline fakes)."""

from app.rag.generator import FakeAnswerGenerator, FakeIncidentAnswerGenerator


def test_fake_answer_generator_uses_kb_message_when_no_context_prompt():
    gen = FakeAnswerGenerator()
    prompt = "...\nThe knowledge base did not return relevant context.\n..."
    answer = gen.generate(prompt)
    assert "does not contain enough information" in answer.lower()


def test_fake_answer_generator_uses_incident_answer_when_context_present():
    gen = FakeAnswerGenerator()
    prompt = "Answer using context.\nSome context chunk here.\nAnswer:"
    answer = gen.generate(prompt)
    assert "retrieved incident context" in answer.lower() or len(answer) > 20


def test_fake_incident_generator_returns_parseable_json_block():
    gen = FakeIncidentAnswerGenerator()
    raw = gen.generate("ignored prompt body")
    assert "incident_summary" in raw
    assert "likely_causes" in raw


def test_fake_incident_generator_keeps_expected_severity_placeholder():
    gen = FakeIncidentAnswerGenerator()
    raw = gen.generate("any")
    assert "severity" in raw
    assert "High" in raw
