#!/usr/bin/env bash
# Stop HW07 stack: tool server process + Open WebUI container.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HW07_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PID_FILE="${HW07_ROOT}/.hw07-tool-server.pid"

if [[ -f "${PID_FILE}" ]]; then
  pid="$(cat "${PID_FILE}")"
  if kill -0 "${pid}" 2>/dev/null; then
    kill "${pid}" || true
    sleep 1
  fi
  rm -f "${PID_FILE}"
  echo "Stopped tool server (pid ${pid})."
else
  echo "No tool server PID file at ${PID_FILE}."
fi

docker compose -f "${HW07_ROOT}/docker-compose.yml" down
echo "Stopped Open WebUI container hw07-open-webui."
