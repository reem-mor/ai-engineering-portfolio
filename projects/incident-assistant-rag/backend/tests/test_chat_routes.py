from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_rejects_empty_question():
    response = client.post("/api/chat", json={"question": "", "top_k": 3})
    assert response.status_code == 422


def test_chat_rejects_invalid_top_k():
    response = client.post("/api/chat", json={"question": "What should I check?", "top_k": 0})
    assert response.status_code == 422


def test_chat_rejects_top_k_above_max():
    response = client.post("/api/chat", json={"question": "What broke?", "top_k": 11})
    assert response.status_code == 422
