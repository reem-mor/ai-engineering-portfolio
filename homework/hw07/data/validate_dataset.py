"""Validate the hw07 AI job-market CSV before uploading it to Open WebUI.

Checks:
  1. CSV exists and is non-empty
  2. CSV parses and has data rows
  3. Useful job-market columns are present (title + at least 3 supporting fields)
  4. Critical fields (job title) are mostly non-empty
  5. Topic is AI jobs / job market / salaries / skills — NOT CVE/NVD or other data

Exit code 0 = valid; 1 = invalid (with reasons printed).

Usage:
    python data/validate_dataset.py [path/to/ai_jobs.csv]
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

DEFAULT_CSV = Path(__file__).resolve().parent / "ai_jobs.csv"

MIN_ROWS = 50
MAX_EMPTY_TITLE_RATIO = 0.05

TITLE_COLUMNS = {"job_title", "title", "role", "position"}
SUPPORTING_COLUMNS = {
    "company", "company_name", "employer",
    "location", "company_location", "country", "city", "employee_residence",
    "salary", "salary_usd", "salary_in_usd", "salary_currency",
    "skills", "required_skills", "skill",
    "experience_level", "years_experience", "seniority",
    "industry", "employment_type", "remote_ratio",
    "posted_date", "posting_date", "job_description", "education_required",
}
FORBIDDEN_TOPIC_COLUMNS = {"cve_id", "cvss", "cvss_score", "cwe", "epss", "vendor_project"}
TOPIC_KEYWORDS = ("job", "salary", "skill", "role", "employ", "remote", "industry")


def validate(csv_path: Path) -> list[str]:
    """Return a list of failure reasons (empty list = valid)."""
    errors: list[str] = []

    if not csv_path.is_file():
        return [f"CSV not found: {csv_path} — run data/download_dataset.py first."]
    if csv_path.stat().st_size == 0:
        return [f"CSV is empty (0 bytes): {csv_path}"]

    with csv_path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.DictReader(handle)
        columns = [c.strip().lower() for c in (reader.fieldnames or [])]
        rows = list(reader)

    if not columns:
        return [f"CSV has no header row: {csv_path}"]
    if len(rows) < MIN_ROWS:
        errors.append(f"Too few data rows: {len(rows)} (need >= {MIN_ROWS}).")

    column_set = set(columns)

    forbidden = column_set & FORBIDDEN_TOPIC_COLUMNS
    if forbidden:
        errors.append(
            f"Wrong topic — CVE/vulnerability columns found: {sorted(forbidden)}. "
            "The hw07 dataset must be AI job-market data."
        )

    title_cols = column_set & TITLE_COLUMNS
    if not title_cols:
        errors.append(f"No job-title column found (expected one of {sorted(TITLE_COLUMNS)}).")

    supporting = column_set & SUPPORTING_COLUMNS
    if len(supporting) < 3:
        errors.append(
            f"Too few job-market columns: {sorted(supporting)} (need >= 3 of "
            "company/location/salary/skills/experience/industry/...)."
        )

    if not any(any(kw in col for kw in TOPIC_KEYWORDS) for col in columns):
        errors.append(
            "Topic check failed: no job/salary/skill-related column names found."
        )

    if title_cols and rows:
        title_col_original = next(
            c for c in (rows[0].keys()) if c and c.strip().lower() in title_cols
        )
        empty = sum(1 for row in rows if not (row.get(title_col_original) or "").strip())
        ratio = empty / len(rows)
        if ratio > MAX_EMPTY_TITLE_RATIO:
            errors.append(
                f"Critical field '{title_col_original}' empty in {empty}/{len(rows)} rows "
                f"({ratio:.1%} > {MAX_EMPTY_TITLE_RATIO:.0%} allowed)."
            )

    if not errors:
        print(f"OK: {csv_path.name} — {len(rows)} rows, {len(columns)} columns")
        print(f"    columns: {', '.join(columns[:12])}{' ...' if len(columns) > 12 else ''}")
        print(f"    job-market columns matched: {sorted(supporting | title_cols)}")
    return errors


def main() -> int:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    errors = validate(csv_path)
    if errors:
        print("DATASET VALIDATION FAILED:", file=sys.stderr)
        for reason in errors:
            print(f"  - {reason}", file=sys.stderr)
        return 1
    print("Dataset validation passed — safe to upload to the Open WebUI knowledge base.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
