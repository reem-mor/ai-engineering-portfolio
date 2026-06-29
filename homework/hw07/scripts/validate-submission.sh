#!/usr/bin/env bash
# Validate HW07 is ready to submit: tests, screenshots, tool server smoke.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HW07_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TOOLS_DIR="${HW07_ROOT}/open-webui-tools"
SCREENSHOTS_DIR="${HW07_ROOT}/screenshots"

echo "=== HW07 submission validation ==="

if [[ -x "${HW07_ROOT}/../../.venv/bin/python" ]] && "${HW07_ROOT}/../../.venv/bin/python" -m pytest --version >/dev/null 2>&1; then
  PYTHON="${HW07_ROOT}/../../.venv/bin/python"
else
  PYTHON="$(command -v python3)"
fi

echo "[1/4] pytest (expect 24 passed)"
(cd "${TOOLS_DIR}" && "${PYTHON}" -m pytest tests -q)

echo "[2/4] screenshot files"
missing=0
for n in 01 02 03 04 05 06; do
  file="${SCREENSHOTS_DIR}/${n}"*
  matches=( ${file} )
  if [[ ! -f "${matches[0]}" ]]; then
    echo "  MISSING: ${SCREENSHOTS_DIR}/${n}-*.png"
    missing=1
  else
    size=$(stat -c%s "${matches[0]}" 2>/dev/null || stat -f%z "${matches[0]}")
    echo "  OK ${matches[0]} (${size} bytes)"
  fi
done
if [[ "${missing}" -eq 1 ]]; then
  echo "Regenerate: homework/hw07/scripts/start-stack.sh --mock-rapidapi && cd homework/hw07/e2e && npx playwright test"
  exit 1
fi

echo "[3/4] tool server smoke (optional — skip if not running)"
if curl -sf --max-time 3 http://127.0.0.1:5005/health >/dev/null 2>&1; then
  curl -sf http://127.0.0.1:5005/health
  echo
  curl -sf -X POST http://127.0.0.1:5005/tools/country_info \
    -H "Content-Type: application/json" \
    -d '{"country_name":"Brazil"}'
  echo
else
  echo "  SKIP — start with: homework/hw07/scripts/start-stack.sh --mock-rapidapi"
fi

echo "[4/4] manual screenshot review"
echo "  Verify 04-kb-chat-answer.png shows TV Show=2676 and Movie=6131 (not skeleton bars)."
echo "  Verify 06-tool-chat-answer.png shows country_info tool call + Brasília answer."
echo "  Verify 05-tool-server-configured.png has ONE tool server entry (reset Docker volume if duplicated)."

echo ""
echo "GitHub path: https://github.com/reem-mor/amdocs-ai-course/tree/main/homework/hw07"
echo "=== Validation complete ==="
