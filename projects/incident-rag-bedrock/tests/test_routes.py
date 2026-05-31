from app.bedrock_client import RagAnswer, Citation
from app.errors import BedrockError


def test_index_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"IncidentIQ" in response.data
    assert b"runbooks" in response.data


def test_ask_empty_question_returns_400(client):
    response = client.post("/ask", data={"question": "   "})
    assert response.status_code == 400
    assert b"Please enter a question" in response.data


def test_ask_oversize_question_returns_400(client):
    response = client.post("/ask", data={"question": "x" * 1000})
    assert response.status_code == 400
    assert b"too long" in response.data


def test_ask_grounded_answer(client, fake_bedrock):
    fake_bedrock.next_response = RagAnswer(
        answer="Restart the auth pod and check the OIDC logs.",
        citations=[
            Citation(snippet="Restart auth pod via kubectl rollout restart.",
                     source_uri="s3://kb-bucket/auth_runbook.md"),
        ],
        session_id="sess-1",
        grounded=True,
    )
    response = client.post("/ask", data={"question": "How do I fix auth?"})
    assert response.status_code == 200
    assert b"Grounded" in response.data
    assert b"Restart the auth pod" in response.data
    assert b"auth_runbook.md" in response.data
    assert fake_bedrock.calls == ["How do I fix auth?"]


def test_ask_no_match_renders_amber_card(client, fake_bedrock):
    fake_bedrock.next_response = RagAnswer(
        answer="I could not find anything in the knowledge base for that question.",
        citations=[],
        session_id=None,
        grounded=False,
    )
    response = client.post("/ask", data={"question": "best pasta recipe?"})
    assert response.status_code == 200
    assert b"No matching context" in response.data


def test_ask_bedrock_error_returns_502(client, fake_bedrock):
    fake_bedrock.next_error = BedrockError("Bedrock is throttling requests.", code="ThrottlingException")
    response = client.post("/ask", data={"question": "anything"})
    assert response.status_code == 502
    assert b"throttling" in response.data.lower()
