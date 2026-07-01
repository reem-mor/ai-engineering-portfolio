"""Tests for data/validate_dataset.py (synthetic CSVs — no Kaggle download needed)."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

HW07_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW07_ROOT / "data"))

from validate_dataset import MIN_ROWS, validate  # noqa: E402

AI_JOBS_HEADER = [
    "job_id", "job_title", "salary_usd", "experience_level", "company_location",
    "company_name", "required_skills", "industry", "remote_ratio", "posting_date",
]


def _write_csv(path: Path, header: list[str], rows: list[list[str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    return path


def _ai_jobs_rows(n: int) -> list[list[str]]:
    return [
        [str(i), "AI Engineer", "120000", "SE", "Israel", "Acme", "Python, PyTorch",
         "Tech", "50", "2025-04-01"]
        for i in range(n)
    ]


def test_valid_ai_jobs_csv_passes(tmp_path: Path) -> None:
    path = _write_csv(tmp_path / "ai_jobs.csv", AI_JOBS_HEADER, _ai_jobs_rows(MIN_ROWS))
    assert validate(path) == []


def test_missing_file_fails(tmp_path: Path) -> None:
    errors = validate(tmp_path / "nope.csv")
    assert errors and "not found" in errors[0]


def test_empty_file_fails(tmp_path: Path) -> None:
    path = tmp_path / "ai_jobs.csv"
    path.write_text("", encoding="utf-8")
    errors = validate(path)
    assert errors and "empty" in errors[0]


def test_too_few_rows_fails(tmp_path: Path) -> None:
    path = _write_csv(tmp_path / "ai_jobs.csv", AI_JOBS_HEADER, _ai_jobs_rows(5))
    assert any("Too few data rows" in e for e in validate(path))


def test_cve_dataset_rejected(tmp_path: Path) -> None:
    header = ["cve_id", "cvss", "summary", "published"]
    rows = [[f"CVE-2024-{i:04d}", "9.8", "bad bug", "2024-01-01"] for i in range(MIN_ROWS)]
    path = _write_csv(tmp_path / "cve.csv", header, rows)
    errors = validate(path)
    assert any("Wrong topic" in e for e in errors)


def test_unrelated_topic_rejected(tmp_path: Path) -> None:
    header = ["temperature", "humidity", "city_code", "reading_time"]
    rows = [["21", "40", "TLV", "2024-01-01"] for _ in range(MIN_ROWS)]
    path = _write_csv(tmp_path / "weather.csv", header, rows)
    errors = validate(path)
    assert any("job-title" in e or "Topic check" in e for e in errors)


def test_empty_titles_rejected(tmp_path: Path) -> None:
    rows = _ai_jobs_rows(MIN_ROWS)
    for row in rows[: MIN_ROWS // 2]:
        row[1] = ""
    path = _write_csv(tmp_path / "ai_jobs.csv", AI_JOBS_HEADER, rows)
    assert any("empty in" in e for e in validate(path))
