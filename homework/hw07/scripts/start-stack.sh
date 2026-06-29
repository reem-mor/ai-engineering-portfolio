#!/usr/bin/env bash
# Start HW07 stack: Open WebUI (Docker) + tool server (host uvicorn).
set -euo pipefail

MOCK_RAPIDAPI=0
TIMEOUT_SEC=120

usage() {
  echo "Usage: $0 [--mock-rapidapi] [--timeout SEC]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mock-rapidapi) MOCK_RAPIDAPI=1; shift ;;
    --timeout) TIMEOUT_SEC="${2:?missing value}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HW07_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TOOLS_DIR="${HW07_ROOT}/open-webui-tools"
REPO_ROOT="$(cd "${HW07_ROOT}/../.." && pwd)"
PID_FILE="${HW07_ROOT}/.hw07-tool-server.pid"
LOG_FILE="${HW07_ROOT}/.hw07-tool-server.log"

if [[ -x "${REPO_ROOT}/.venv/bin/python" ]]; then
  PYTHON="${REPO_ROOT}/.venv/bin/python"
else
  PYTHON="$(command -v python3)"
fi

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "Required command not found: $1" >&2; exit 1; }
}

wait_http_ok() {
  local url="$1"
  local deadline=$((SECONDS + TIMEOUT_SEC))
  while (( SECONDS < deadline )); do
    if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done
  return 1
}

port_in_use() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn | grep -q ":${port} "
  else
    lsof -i ":${port}" -sTCP:LISTEN >/dev/null 2>&1
  fi
}

echo "=== HW07 stack preflight ==="
require_cmd docker
require_cmd curl
require_cmd ollama

if ! ollama list >/dev/null 2>&1; then
  echo "Ollama is not running. Start Ollama and run: ollama pull llama3.2:3b" >&2
  exit 1
fi

if port_in_use 3001 && ! docker ps --format '{{.Names}}' | grep -qx 'hw07-open-webui'; then
  echo "Port 3001 is in use by a non-HW07 process." >&2
  exit 1
fi
if port_in_use 5005 && [[ ! -f "${PID_FILE}" ]]; then
  echo "Port 5005 is in use and no HW07 PID file found at ${PID_FILE}." >&2
  exit 1
fi

echo "Starting Open WebUI via docker compose..."
docker compose -f "${HW07_ROOT}/docker-compose.yml" up -d

if ! wait_http_ok "http://localhost:3001"; then
  echo "Open WebUI did not become ready at http://localhost:3001 within ${TIMEOUT_SEC}s" >&2
  exit 1
fi
echo "Open WebUI ready: http://localhost:3001"

if [[ ! -f "${TOOLS_DIR}/.env" ]]; then
  cp "${TOOLS_DIR}/.env.example" "${TOOLS_DIR}/.env"
  echo "Created ${TOOLS_DIR}/.env from .env.example — set RAPIDAPI_KEY for live API calls."
fi

if [[ -f "${PID_FILE}" ]]; then
  old_pid="$(cat "${PID_FILE}")"
  if kill -0 "${old_pid}" 2>/dev/null; then
    kill "${old_pid}" || true
    sleep 1
  fi
  rm -f "${PID_FILE}"
fi

export HW07_MOCK_RAPIDAPI="${MOCK_RAPIDAPI}"
if [[ "${MOCK_RAPIDAPI}" == "1" ]]; then
  echo "HW07_MOCK_RAPIDAPI=1 (deterministic tool responses)"
fi

echo "Starting tool server on :5005..."
(
  cd "${TOOLS_DIR}"
  nohup "${PYTHON}" -m uvicorn tools_server:app --host 0.0.0.0 --port 5005 \
    >"${LOG_FILE}" 2>&1 &
  echo $! >"${PID_FILE}"
)

if ! wait_http_ok "http://localhost:5005/health"; then
  echo "Tool server failed to start. Log tail:" >&2
  tail -n 40 "${LOG_FILE}" >&2 || true
  exit 1
fi

health="$(curl -sf http://localhost:5005/health)"
echo "Tool server ready: http://localhost:5005"
echo "  health=${health}"
echo ""
echo "=== Stack running ==="
echo "  Open WebUI:        http://localhost:3001"
echo "  Tool server docs:  http://localhost:5005/docs"
echo "  Tool URL (Docker): http://host.docker.internal:5005"
echo "  Tool server log:   ${LOG_FILE}"
echo ""
echo "Run Playwright: cd homework/hw07/e2e && npm install && npx playwright test"
echo "Stop stack:     homework/hw07/scripts/stop-stack.sh"
