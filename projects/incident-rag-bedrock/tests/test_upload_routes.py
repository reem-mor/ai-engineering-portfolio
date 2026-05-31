"""Route tests for POST /documents/upload."""
from __future__ import annotations

import io

import pytest

from app.errors import BedrockError
from app.upload_service import UploadResult


class _FakeUploadService:
    def __init__(self):
        self.next_result: UploadResult | None = None
        self.next_error: BedrockError | None = None
        self.calls: list[tuple[str | None, bytes, bool]] = []

    def upload(self, filename, body, *, sync_kb: bool):
        self.calls.append((filename, body, sync_kb))
        if self.next_error is not None:
            raise self.next_error
        return self.next_result


@pytest.fixture
def upload_service():
    return _FakeUploadService()


@pytest.fixture
def upload_app(app, upload_service):
    app.extensions["upload_service"] = upload_service
    app.config.update(
        S3_BUCKET="reem-amdocs-ai-artifacts-3331",
        S3_PREFIX="projects/incident-rag-bedrock/data/sample_documents",
        BEDROCK_DATA_SOURCE_ID="YICXAB6WOG",
        MAX_UPLOAD_BYTES=1024,
    )
    return app


@pytest.fixture
def upload_client(upload_app):
    return upload_app.test_client()


def _file(name: str, content: bytes):
    return (io.BytesIO(content), name)


def test_upload_success_html(upload_client, upload_service):
    upload_service.next_result = UploadResult(
        filename="note.txt",
        s3_key="projects/incident-rag-bedrock/data/sample_documents/x_note.txt",
        s3_uri="s3://bucket/projects/incident-rag-bedrock/data/sample_documents/x_note.txt",
        size_bytes=12,
        sync_started=True,
        ingestion_job_id="job-1",
    )
    resp = upload_client.post(
        "/documents/upload",
        data={"document": _file("note.txt", b"hello world"), "sync_kb": "on"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert b"Document saved" in resp.data
    assert b"ingestion job started" in resp.data
    assert upload_service.calls[0][2] is True


def test_upload_unsupported_type_400(upload_client, upload_service):
    upload_service.next_error = BedrockError("Unsupported", code="unsupported_type")
    resp = upload_client.post(
        "/documents/upload",
        data={"document": _file("bad.exe", b"x")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
    assert b"Upload failed" in resp.data


def test_upload_s3_error_502(upload_client, upload_service):
    upload_service.next_error = BedrockError("S3 denied", code="AccessDenied")
    resp = upload_client.post(
        "/documents/upload",
        data={"document": _file("note.txt", b"data")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 502


def test_upload_json_format(upload_client, upload_service):
    upload_service.next_result = UploadResult(
        filename="a.md",
        s3_key="k",
        s3_uri="s3://b/k",
        size_bytes=3,
        sync_started=False,
    )
    resp = upload_client.post(
        "/documents/upload?format=json",
        data={"document": _file("a.md", b"# x")},
        content_type="multipart/form-data",
        headers={"Accept": "application/json"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["filename"] == "a.md"


def test_upload_disabled_400(upload_client, upload_app, upload_service):
    upload_app.config["S3_BUCKET"] = ""
    upload_service.next_error = BedrockError("not configured", code="upload_disabled")
    resp = upload_client.post(
        "/documents/upload",
        data={"document": _file("a.txt", b"x")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400
