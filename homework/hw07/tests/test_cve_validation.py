"""Unit tests for CVE validation and normalization helpers."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

import tools_server


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("CVE-2021-44228", "CVE-2021-44228"),
        ("cve-2021-44228", "CVE-2021-44228"),
        ("  CVE-2020-1234  ", "CVE-2020-1234"),
    ],
)
def test_validate_cve_id_accepts_valid(raw: str, expected: str) -> None:
    assert tools_server.validate_cve_id(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "CVE-2021", "2021-44228", "CVE-21-44228", "CVE-2021-abc"],
)
def test_validate_cve_id_rejects_invalid(raw: str) -> None:
    with pytest.raises(HTTPException) as exc_info:
        tools_server.validate_cve_id(raw)
    assert exc_info.value.status_code == 422
