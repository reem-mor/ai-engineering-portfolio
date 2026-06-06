"""One-off generator for REPOSITORY_INVENTORY.md (audit phase)."""
from __future__ import annotations

from pathlib import Path

root = Path(__file__).resolve().parents[2]
skip_dirs = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
}


def classify(p: Path) -> tuple[str, str, str, str, str, str]:
    rel = p.relative_to(root).as_posix()
    name = p.name
    if name in {".env", ".env.production"} or name.endswith(".pem"):
        return (
            "Secret risk",
            "Local env / credentials",
            "Runtime",
            "No",
            "No",
            "Keep gitignored; never commit",
        )
    if name in {".ec2_instance_id.txt", ".sg_id.txt", "lambda-out.json", "pytest_output.txt"}:
        return (
            "Temporary/debug file",
            "Local AWS/debug artifact",
            "None",
            "Yes",
            "No",
            "Delete candidate (after approval)",
        )
    if "app/static/spa/assets" in rel and name.endswith((".js", ".css")):
        return (
            "Generated but required for deployment",
            "Vite production bundle",
            "Flask spa.py, Dockerfile",
            "Yes",
            "Yes (until rebuild)",
            "Keep; rebuild via npm run build",
        )
    if rel.startswith("app/") and rel.endswith(".py"):
        return (
            "Required runtime source",
            "Flask app module",
            "routes, tests, rag_factory",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("tests/"):
        return ("Required test", "Pytest module", "pytest", "No", "Yes", "Keep")
    if rel.startswith("action_groups/"):
        return (
            "Required runtime source",
            "Lambda action group",
            "setup_enrichment_lambdas.py",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("scripts/") and p.suffix == ".py":
        return (
            "Required configuration",
            "Ops/setup script",
            "README, docs",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("docs/review/"):
        return ("Required documentation", "Audit output", "This review", "No", "Yes", "Keep")
    if rel.startswith("docs/"):
        return (
            "Required documentation",
            "Project docs",
            "README links",
            "No",
            "Mostly yes",
            "Keep; archive stale after approval",
        )
    if rel.startswith("evaluation/"):
        return (
            "Required test",
            "Eval/smoke artifacts",
            "smoke scripts",
            "Mixed",
            "Yes",
            "Keep",
        )
    if rel.startswith("data/sample_documents/"):
        return (
            "Required runtime source",
            "KB corpus (local + S3)",
            "local_rag, KB sync",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("knowledge_base/"):
        return (
            "Required runtime source",
            "Docker-packaged runbooks",
            "Dockerfile COPY",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("infra/"):
        return (
            "Required configuration",
            "AWS/IaC helpers",
            "setup scripts",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("frontend/"):
        return (
            "Required runtime source",
            "React SPA source",
            "Docker build stage",
            "No",
            "Yes",
            "Keep",
        )
    if name in {
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt",
        "wsgi.py",
        "pytest.ini",
        ".gitignore",
        ".dockerignore",
        ".env.example",
    }:
        return (
            "Required configuration",
            "Project infra",
            "Docker/pytest",
            "No",
            "Yes",
            "Keep",
        )
    if rel.startswith("screenshots/"):
        return (
            "Required documentation",
            "Submission screenshots",
            "README",
            "No",
            "Optional",
            "Keep if referenced",
        )
    return ("Needs verification", "Misc project file", "TBD", "Unknown", "Verify", "Review manually")


rows: list[tuple[str, ...]] = []
for p in sorted(root.rglob("*")):
    if not p.is_file():
        continue
    if any(part in skip_dirs for part in p.parts):
        continue
    rows.append((p.relative_to(root).as_posix(), *classify(p)))

out = root / "docs" / "review" / "REPOSITORY_INVENTORY.md"
lines = [
    "# PITER AiOps — Repository Inventory",
    "",
    "Read-only audit generated 2026-06-06. Excludes `.git`, `.venv`, `node_modules`, `__pycache__`, `.pytest_cache`, and other generated caches.",
    "",
    f"**Total tracked files:** {len(rows)}",
    "",
    "| Path | Type | Purpose | Referenced by | Generated? | Required? | Recommendation |",
    "| ---- | ---- | ------- | ------------- | ---------- | --------- | -------------- |",
]
for r in rows:
    lines.append(
        f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} | {r[6]} |"
    )
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {len(rows)} rows to {out}")
