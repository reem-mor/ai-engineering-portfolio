"""Fetch CVE records from NVD API into data/cve.csv (fallback when Kaggle is unavailable)."""

from __future__ import annotations

import csv
import time
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent / "cve.csv"
KEYWORDS = ["Apache Struts", "Apache Log4j", "Apache HTTP Server"]


def fetch_keyword(keyword: str, rows: list[dict], seen: set[str], max_pages: int = 3) -> None:
    start = 0
    per_page = 100
    for _ in range(max_pages):
        response = httpx.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={"keywordSearch": keyword, "startIndex": start, "resultsPerPage": per_page},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        for item in data.get("vulnerabilities", []):
            cve = item.get("cve", {})
            cve_id = cve.get("id", "")
            if not cve_id or cve_id in seen:
                continue
            seen.add(cve_id)
            description = ""
            for desc in cve.get("descriptions", []):
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break
            cvss = None
            metrics = cve.get("metrics", {})
            for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
                arr = metrics.get(key) or []
                if arr:
                    cvss = arr[0].get("cvssData", {}).get("baseScore")
                    break
            rows.append(
                {
                    "cve_id": cve_id,
                    "description": description,
                    "cvss": cvss if cvss is not None else "",
                    "published": cve.get("published", ""),
                    "keyword": keyword,
                }
            )
        total = data.get("totalResults", 0)
        start += per_page
        if start >= total or start >= max_pages * per_page:
            break
        time.sleep(6)


def main() -> int:
    rows: list[dict] = []
    seen: set[str] = set()
    for keyword in KEYWORDS:
        fetch_keyword(keyword, rows, seen)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["cve_id", "description", "cvss", "published", "keyword"]
        )
        writer.writeheader()
        writer.writerows(rows)

    struts_count = sum(1 for row in rows if "struts" in row["description"].lower())
    print(f"OK: wrote {OUT} with {len(rows)} rows ({struts_count} Struts-related)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
