#!/usr/bin/env bash
# Memora Graph Server Starter (modo persistente para UI local)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
MEMORA_BIN="${ROOT_DIR}/.opencode/.venv-memora/bin/memora-server"
MEMORA_PY="${ROOT_DIR}/.opencode/.venv-memora/bin/python"
LOG_FILE="${ROOT_DIR}/.opencode/memora-graph.log"
PID_FILE="${ROOT_DIR}/.opencode/memora-graph.pid"
OVERRIDE_DIR="${ROOT_DIR}/.opencode/memora-overrides/graph"
GRAPH_PORT=8765
MCP_PORT=8000

if [[ ! -x "${MEMORA_BIN}" ]]; then
  echo "Memora runtime nao encontrado em ${MEMORA_BIN}"
  echo "Instale com:"
  echo "  python3 -m venv .opencode/.venv-memora"
  echo "  .opencode/.venv-memora/bin/python -m pip install 'git+https://github.com/agentic-mcp-tools/memora.git'"
  exit 1
fi

export MEMORA_DB_PATH="${ROOT_DIR}/.opencode/memory/memoria.db"
export MEMORA_ALLOW_ANY_TAG=1
export MEMORA_GRAPH_PORT="${GRAPH_PORT}"

listening_pids() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -t -iTCP:"${port}" -sTCP:LISTEN 2>/dev/null | sort -u || true
    return
  fi
  if command -v ss >/dev/null 2>&1; then
    ss -ltnp "sport = :${port}" 2>/dev/null \
      | grep -o 'pid=[0-9]\+' \
      | sed 's/pid=//' \
      | sort -u || true
    return
  fi
}

stop_pid() {
  local pid="$1"
  if [[ -z "${pid}" ]]; then
    return 0
  fi
  if ! kill -0 "${pid}" 2>/dev/null; then
    return 0
  fi
  kill "${pid}" 2>/dev/null || true
  for _ in $(seq 1 10); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 0
    fi
    sleep 1
  done
  kill -9 "${pid}" 2>/dev/null || true
}

cleanup_existing_instance() {
  local old_pid=""
  if [[ -f "${PID_FILE}" ]]; then
    old_pid="$(tr -d '[:space:]' < "${PID_FILE}" || true)"
    if [[ -n "${old_pid}" ]]; then
      echo "Stopping existing Memora process from PID file: ${old_pid}"
      stop_pid "${old_pid}"
    fi
    rm -f "${PID_FILE}"
  fi

  for port in "${GRAPH_PORT}" "${MCP_PORT}"; do
    local pids
    pids="$(listening_pids "${port}")"
    if [[ -n "${pids}" ]]; then
      echo "Cleaning listeners on port ${port}: ${pids//$'\n'/ }"
      while IFS= read -r pid; do
        stop_pid "${pid}"
      done <<< "${pids}"
    fi
  done
}

detect_memora_graph_dir() {
  if [[ ! -x "${MEMORA_PY}" ]]; then
    return 1
  fi
  "${MEMORA_PY}" - <<'PY'
import inspect
from pathlib import Path
import memora.graph
print(Path(inspect.getfile(memora.graph)).resolve().parent)
PY
}

sync_memora_overrides() {
  if [[ ! -d "${OVERRIDE_DIR}" ]]; then
    return 0
  fi
  local graph_dir
  graph_dir="$(detect_memora_graph_dir 2>/dev/null || true)"
  if [[ -z "${graph_dir}" || ! -d "${graph_dir}" ]]; then
    echo "Memora graph dir not detected; skipping overrides."
    return 0
  fi
  local synced=0
  for file in index.html data.py server.py; do
    if [[ -f "${OVERRIDE_DIR}/${file}" ]]; then
      cp "${OVERRIDE_DIR}/${file}" "${graph_dir}/${file}"
      synced=1
    fi
  done
  if [[ "${synced}" -eq 1 ]]; then
    echo "Applied memora overrides from ${OVERRIDE_DIR}"
  fi
}

echo "Starting Memora Graph Server..."
echo "Graph UI: http://127.0.0.1:${GRAPH_PORT}/graph"
echo "MCP SSE: http://127.0.0.1:${MCP_PORT}/sse"
echo ""

cd "${ROOT_DIR}"

sync_memora_overrides
cleanup_existing_instance

setsid env \
  MEMORA_DB_PATH="${MEMORA_DB_PATH}" \
  MEMORA_ALLOW_ANY_TAG="${MEMORA_ALLOW_ANY_TAG}" \
  MEMORA_GRAPH_PORT="${MEMORA_GRAPH_PORT}" \
  "${MEMORA_BIN}" --transport sse --host 127.0.0.1 --port "${MCP_PORT}" \
  </dev/null >"${LOG_FILE}" 2>&1 &

PID=$!
echo "${PID}" > "${PID_FILE}"

sleep 2

# Aguarda subida do Graph por ate 20s (cold start pode ser lento)
for _ in $(seq 1 10); do
  if curl -fsS --max-time 5 "http://127.0.0.1:${GRAPH_PORT}/graph" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 2
done

if [[ "${READY:-0}" -eq 1 ]]; then
  echo "Graph server started (PID: ${PID})"
  echo "Log: ${LOG_FILE}"
  echo "To stop: kill ${PID}"
else
  echo "Falha ao validar Graph UI. Verifique o log em ${LOG_FILE}"
  kill "${PID}" 2>/dev/null || true
  rm -f "${PID_FILE}"
  exit 1
fi
