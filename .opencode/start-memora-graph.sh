#!/bin/bash
# ============================================
# Memora Graph Server Starter
# Inicia o servidor de visualização do Graph
# ============================================

export MEMORA_DB_PATH="G:/projetos/docs-copy/.opencode/memory/memoria.db"
export MEMORA_ALLOW_ANY_TAG=1
export MEMORA_GRAPH_PORT=8765

echo "Starting Memora Graph Server..."
echo "Graph UI: http://localhost:8765/graph"
echo ""

cd "G:/projetos/docs-copy"

C:/Users/papa/AppData/Local/Programs/Python/Python313/python.exe -m memora --graph-port 8765 &

PID=$!
echo "Graph server started (PID: $PID)"
echo ""
echo "To stop: kill $PID"
