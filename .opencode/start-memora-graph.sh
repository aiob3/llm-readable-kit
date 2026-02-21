#!/usr/bin/env bash
# Memora Graph Server Starter (modo persistente para UI local)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"
MEMORA_BIN="${ROOT_DIR}/.opencode/.venv-memora/bin/memora-server"
LOG_FILE="${ROOT_DIR}/.opencode/memora-graph.log"
PID_FILE="${ROOT_DIR}/.opencode/memora-graph.pid"

if [[ ! -x "${MEMORA_BIN}" ]]; then
  echo "Memora runtime nao encontrado em ${MEMORA_BIN}"
  echo "Instale com:"
  echo "  python3 -m venv .opencode/.venv-memora"
  echo "  .opencode/.venv-memora/bin/python -m pip install 'git+https://github.com/agentic-mcp-tools/memora.git'"
  exit 1
fi

export MEMORA_DB_PATH="${ROOT_DIR}/.opencode/memory/memoria.db"
export MEMORA_ALLOW_ANY_TAG=1
export MEMORA_GRAPH_PORT=8765

echo "Starting Memora Graph Server..."
echo "Graph UI: http://127.0.0.1:8765/graph"
echo "MCP SSE: http://127.0.0.1:8000/sse"
echo ""

cd "${ROOT_DIR}"

if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
  echo "Memora Graph ja esta em execucao (PID $(cat "${PID_FILE}"))."
  exit 0
fi

setsid env \
  MEMORA_DB_PATH="${MEMORA_DB_PATH}" \
  MEMORA_ALLOW_ANY_TAG="${MEMORA_ALLOW_ANY_TAG}" \
  MEMORA_GRAPH_PORT="${MEMORA_GRAPH_PORT}" \
  "${MEMORA_BIN}" --transport sse --host 127.0.0.1 --port 8000 \
  </dev/null >"${LOG_FILE}" 2>&1 &

PID=$!
echo "${PID}" > "${PID_FILE}"

sleep 2

# Aguarda subida do Graph por ate 20s (cold start pode ser lento)
for _ in $(seq 1 10); do
  if curl -fsS --max-time 5 http://127.0.0.1:8765/graph >/dev/null 2>&1; then
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
