"""JSON API routes for the React SPA."""

from app.bedrock_client import Citation, RagAnswer


def _fake_answer():
    return RagAnswer(
        answer="Check runbook_db_cpu.md for CPU alerts.",
        citations=[
            Citation(
                snippet="Step 1: pg_stat_activity",
                source_uri="s3://bucket/runbook.md",
                source_label="runbook_db_cpu.md",
                index=1,
            )
        ],
        session_id="sess-1",
        grounded=True,
        latency_ms=120,
        matched_runbook="runbook_db_cpu.md",
    )


def test_api_bootstrap(client):
    response = client.get("/api/bootstrap")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert "examples" in data
    assert len(data["examples"]) > 0
    assert isinstance(data["example_groups"], dict)
    assert sum(len(v) for v in data["example_groups"].values()) >= len(data["examples"])
    assert "workflow_alerts" in data
    assert len(data["workflow_alerts"]) == 6
    assert "max_len" in data
    assert "csrf_token" in data


def test_api_health_alias(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_api_workflow_triage_json(client, fake_bedrock):
    fake_bedrock.next_response = _fake_answer()
    response = client.post(
        "/api/workflow/triage",
        json={"alert_id": "A-2041", "question": ""},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["result"]["grounded"] is True
    assert data["actions"]
    assert data["effective_decision"]
    assert fake_bedrock.calls


def test_ask_json_body(client, fake_bedrock):
    fake_bedrock.next_response = _fake_answer()
    response = client.post("/ask", json={"question": "What is the runbook for high CPU?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert "answer" in data
    assert "answer_sections" in data
    assert data["citations"]
    assert "preview" in data["citations"][0]


def test_api_chat_alias(client, fake_bedrock):
    fake_bedrock.next_response = _fake_answer()
    response = client.post("/api/chat", json={"message": "What is the runbook for high CPU?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["answer"]
    assert data["memory"]["last_question"] == "What is the runbook for high CPU?"


def test_api_chat_rejects_empty_message(client):
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 400
    data = response.get_json()
    assert data["ok"] is False
    assert data["reason"] == "empty_question"


def test_api_incidents_analyze_alias(client, fake_bedrock):
    fake_bedrock.next_response = _fake_answer()
    response = client.post(
        "/api/incidents/analyze",
        json={
            "service": "postgres",
            "environment": "production",
            "severity": "P2",
            "symptom": "Postgres CPU is 95 percent on the primary database",
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["session_id"]
    assert data["piter"]
    assert set(data["piter"]) >= {"priority", "investigation", "triage", "escalation", "resolution"}
    assert "business_impact" in data
    assert "next_action" in data
    assert "confidence" in data
    assert isinstance(data["sources"], list)
    assert isinstance(data["tool_results"], list)


def test_api_tools_status(client):
    response = client.get("/api/tools/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert len(data["tools"]) == 4
    names = {t["name"] for t in data["tools"]}
    assert "Recent deployment lookup" in names
    assert "Service context lookup" in names
    assert "Similar incidents lookup" in names
    assert "Escalation recommendation" in names


def test_api_history_get_and_delete(client, fake_bedrock):
    from app.services import chat_history

    chat_history.reset()
    fake_bedrock.next_response = _fake_answer()
    client.post("/api/chat", json={"message": "What is the runbook for high CPU?"})
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["count"] >= 2
    assert data["messages"][0]["role"] == "user"

    cleared = client.delete("/api/history")
    assert cleared.status_code == 200
    assert cleared.get_json()["cleared"] >= 2
    empty = client.get("/api/history")
    assert empty.get_json()["count"] == 0


def test_api_chat_response_shape(client, fake_bedrock):
    fake_bedrock.next_response = _fake_answer()
    response = client.post("/api/chat", json={"message": "What is the runbook for high CPU?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["piter"]
    assert set(data["piter"]) >= {"priority", "investigation", "triage", "escalation", "resolution"}
    assert "business_impact" in data
    assert "next_action" in data
    assert "confidence" in data
    assert isinstance(data["sources"], list)
    assert isinstance(data["tool_results"], list)
