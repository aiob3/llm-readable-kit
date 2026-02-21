@echo off
setlocal enabledelayedexpansion
REM Memora Graph Server Starter (modo persistente)

set ROOT_DIR=%~dp0..
set GRAPH_PORT=8765
set MCP_PORT=8000
set MEMORA_DB_PATH=%ROOT_DIR%\.opencode\memory\memoria.db
set MEMORA_ALLOW_ANY_TAG=1
set MEMORA_GRAPH_PORT=%GRAPH_PORT%
set PID_FILE=%ROOT_DIR%\.opencode\memora-graph.pid
set LOG_FILE=%ROOT_DIR%\.opencode\memora-graph.log

set MEMORA_CMD=%ROOT_DIR%\.opencode\.venv-memora\Scripts\memora-server.exe
if not exist "%MEMORA_CMD%" (
    where memora-server >nul 2>nul
    if errorlevel 1 (
        echo Memora runtime nao encontrado.
        echo Instale o runtime e tente novamente.
        exit /b 1
    ) else (
        set MEMORA_CMD=memora-server
    )
)

echo Starting Memora Graph Server...
echo Graph UI: http://127.0.0.1:%GRAPH_PORT%/graph
echo MCP SSE: http://127.0.0.1:%MCP_PORT%/sse
echo.

start "" /b cmd /c ""%MEMORA_CMD%" --transport sse --host 127.0.0.1 --port %MCP_PORT% 1>>"%LOG_FILE%" 2>&1"

set READY=0
for /l %%i in (1,1,10) do (
    timeout /t 2 /nobreak >nul
    curl -fsS --max-time 5 http://127.0.0.1:%GRAPH_PORT%/graph >nul 2>nul
    if not errorlevel 1 (
        set READY=1
        goto :ready
    )
)

:ready
if "%READY%"=="1" (
    echo Graph server started successfully!
    echo Access: http://127.0.0.1:%GRAPH_PORT%/graph
) else (
    echo Falha ao validar Graph UI. Verifique o log em:
    echo %LOG_FILE%
    exit /b 1
)
