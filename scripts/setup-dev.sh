#!/usr/bin/env bash
# Bootstrap root venv, dev tools, lecture-08 MCP deps, and .env from example.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Python venv (.venv)"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -r requirements-dev.txt

echo "==> Lecture 08 MCP server deps"
LEC08="$ROOT/lectures/08_mcp"
python3 -m venv "$LEC08/.venv"
"$LEC08/.venv/bin/pip" install -r "$LEC08/requirements.txt"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example — fill in your keys locally."
else
  echo ".env already exists — skipped."
fi

cat <<'EOF'

Done. Next:
  source .venv/bin/activate
  ruff check .
  See docs/AGENT-TOOLING.md for MCP setup (.mcp.json at repo root).
EOF
