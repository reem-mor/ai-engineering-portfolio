"""Tests for knowledge browse API endpoints."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def test_bootstrap_endpoint(client: TestClient) -> None:
    response = client.get("/api/bootstrap")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "incidents" in data
    assert "recent_incidents" in data
    assert "sops" in data
    assert "resources" in data
    assert len(data["recent_incidents"]) >= 1
    assert data["stats"]["total_incidents"] == 30


def test_incident_detail(client: TestClient) -> None:
    response = client.get("/api/incidents/INC-006")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "INC-006"
    assert "CrashLoopBackOff" in data["title"]
    assert len(data["triage_steps"]) >= 3


def test_sop_detail(client: TestClient) -> None:
    response = client.get("/api/sops/SOP-MQ-001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "SOP-MQ-001"
    assert "Kafka" in data["title"]
    assert len(data["steps"]) >= 3


def test_incident_detail_not_found(client: TestClient) -> None:
    response = client.get("/api/incidents/INC-999")
    assert response.status_code == 404


def test_recent_incidents(client: TestClient) -> None:
    response = client.get("/api/incidents/recent?limit=4")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 4
    assert rows[0]["id"].startswith("INC-")


def test_recent_before_detail_route(client: TestClient) -> None:
    """Ensure /incidents/recent is not captured by /incidents/{id}."""
    response = client.get("/api/incidents/recent")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
