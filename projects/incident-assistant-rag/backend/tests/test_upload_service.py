"""UploadService edge cases (async core without pytest-asyncio)."""

import asyncio
from io import BytesIO

import pytest
from starlette.datastructures import UploadFile

from app.core.config import settings
from app.services.upload_service import UploadService


async def _save(upload: UploadFile) -> tuple[str, int]:
    return await UploadService().save_upload(upload)


def test_upload_service_saves_file_and_returns_size(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "raw_data_dir", tmp_path / "raw")
    upload = UploadFile(filename="notes.md", file=BytesIO(b"four"))
    saved, size = asyncio.run(_save(upload))
    assert saved.endswith(".md")
    assert size == 4
    assert (tmp_path / "raw" / saved).read_bytes() == b"four"


def test_upload_service_rejects_missing_filename(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "raw_data_dir", tmp_path / "raw")
    upload = UploadFile(filename="", file=BytesIO(b"x"))
    with pytest.raises(ValueError, match="filename"):
        asyncio.run(_save(upload))


def test_upload_service_rejects_oversized_upload(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "raw_data_dir", tmp_path / "raw")
    monkeypatch.setattr(settings, "max_upload_size_bytes", 4)
    upload = UploadFile(filename="big.txt", file=BytesIO(b"12345678"))
    with pytest.raises(ValueError, match="too large"):
        asyncio.run(_save(upload))
