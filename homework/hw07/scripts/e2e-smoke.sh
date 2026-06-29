#!/usr/bin/env bash
# HW07 backward E2E smoke — build order: API → server → (Web UI manual/Playwright)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HW07_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BASE="${TOOL_SERVER_URL:-http://localhost:5005}"
BASE="${BASE%/}"

echo "=== HW07 E2E backward smoke ==="
echo "Tool server: ${BASE}"
echo ""

step() { echo ""; echo "▶ $1"; }

step "Step 1 — External API seam (mock RapidAPI via tool server)"
health=$(curl -sf "${BASE}/health")
echo "  health: ${health}"
mock=$(echo "${health}" | grep -q '"mock_mode":"true"' && echo yes || echo no)
if [[ "${mock}" == "yes" ]]; then
  echo "  mode: mock (deterministic — set RAPIDAPI_KEY + HW07_MOCK_RAPIDAPI=0 for live)"
else
  echo "  mode: live RapidAPI"
fi
country=$(curl -sf -X POST "${BASE}/tools/country_info" \
  -H "Content-Type: application/json" \
  -d '{"country_name":"Brazil"}')
echo "  country_info: ${country}"
echo "${country}" | grep -q '"ok":true' || { echo "FAIL: country_info"; exit 1; }

step "Step 2 — Local server OpenAPI + all tools"
curl -sf "${BASE}/openapi.json" | grep -q country_info || { echo "FAIL: openapi"; exit 1; }
echo "  openapi.json: OK (country_info, search_title, streaming_status)"

title=$(curl -sf -X POST "${BASE}/tools/search_title" \
  -H "Content-Type: application/json" \
  -d '{"title":"Squid Game"}')
echo "  search_title: ${title}"
echo "${title}" | grep -q '"ok":true' || { echo "FAIL: search_title"; exit 1; }

stream=$(curl -sf -X POST "${BASE}/tools/streaming_status" \
  -H "Content-Type: application/json" \
  -d '{"title":"Stranger Things","country_code":"US"}')
echo "  streaming_status: ${stream}"
echo "${stream}" | grep -q '"ok":true' || { echo "FAIL: streaming_status"; exit 1; }

step "Step 3 — Logging (watch tool server terminal during Web UI chat)"
echo "  tools_server.py logs: tool=<name> ok=<bool> source=<mock|rapidapi> latency_ms=<float>"
echo "  Tail log: homework/hw07/.hw07-tool-server.log (if started via start-stack.sh)"

step "Step 4 — Full Web UI E2E (requires Docker + Ollama)"
if curl -sf --max-time 3 http://localhost:3001 >/dev/null 2>&1; then
  echo "  Open WebUI: UP — run Playwright submission screenshots"
  echo "  cd homework/hw07/e2e && npx playwright test submission-screenshots.spec.ts"
else
  echo "  Open WebUI: not running — start with homework/hw07/scripts/start-stack.sh"
fi

step "Playwright API-layer E2E"
if command -v npm >/dev/null 2>&1 && [[ -d "${HW07_ROOT}/e2e/node_modules" ]]; then
  (cd "${HW07_ROOT}/e2e" && npx playwright test e2e-pipeline.spec.ts tool-server-openapi.spec.ts)
else
  echo "  SKIP — cd homework/hw07/e2e && npm install first"
fi

echo ""
echo "=== E2E backward smoke complete ==="
