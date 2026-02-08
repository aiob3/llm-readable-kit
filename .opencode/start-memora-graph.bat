@echo off
REM ============================================
REM Memora Graph Server Starter
REM Inicia o servidor de visualização do Graph
REM em background e mantém rodando
REM ============================================

set GRAPH_PORT=8765
set MEMORA_DB_PATH=G:\projetos\docs-copy\.opencode\memory\memoria.db
set MEMORA_ALLOW_ANY_TAG=1

echo Starting Memora Graph Server on port %GRAPH_PORT%...
echo Graph UI: http://localhost:%GRAPH_PORT%/graph
echo.

start /b cmd /c "C:\Users\papa\AppData\Local\Programs\Python\Python313\python.exe -m memora --graph-port %GRAPH_PORT%"

timeout /t 3 /nobreak >nul

curl -s -o nul -w "%%{http_code}" http://localhost:%GRAPH_PORT%/graph 2>nul
if %errorlevel%==200 (
    echo Graph server started successfully!
    echo Access: http://localhost:%GRAPH_PORT%/graph
) else (
    echo Warning: Could not verify graph server startup
)

echo.
echo Press any key to close this window (server will continue running)...
pause >nul
