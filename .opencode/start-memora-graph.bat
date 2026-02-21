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
set OVERRIDE_DIR=%ROOT_DIR%\.opencode\memora-overrides\graph
set VENV_PY=%ROOT_DIR%\.opencode\.venv-memora\Scripts\python.exe

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

call :sync_overrides
call :cleanup_existing

set NEW_PID=
for /f %%p in ('powershell -NoProfile -Command "$p = Start-Process -FilePath \"%MEMORA_CMD%\" -ArgumentList ''--transport'',''sse'',''--host'',''127.0.0.1'',''--port'',''%MCP_PORT%'' -RedirectStandardOutput \"%LOG_FILE%\" -RedirectStandardError \"%LOG_FILE%\" -PassThru; $p.Id"') do (
    set NEW_PID=%%p
)

if "%NEW_PID%"=="" (
    echo Falha ao iniciar processo do Memora.
    exit /b 1
)

echo %NEW_PID%>"%PID_FILE%"

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
    echo Graph server started successfully! ^(PID %NEW_PID%^)
    echo Access: http://127.0.0.1:%GRAPH_PORT%/graph
) else (
    echo Falha ao validar Graph UI. Verifique o log em:
    echo %LOG_FILE%
    taskkill /pid %NEW_PID% /f /t >nul 2>nul
    del /f /q "%PID_FILE%" >nul 2>nul
    exit /b 1
)

exit /b 0

:cleanup_existing
if exist "%PID_FILE%" (
    set OLD_PID=
    set /p OLD_PID=<"%PID_FILE%"
    if not "!OLD_PID!"=="" (
        echo Stopping existing Memora process from PID file: !OLD_PID!
        taskkill /pid !OLD_PID! /f /t >nul 2>nul
    )
    del /f /q "%PID_FILE%" >nul 2>nul
)

call :kill_port %GRAPH_PORT%
call :kill_port %MCP_PORT%
exit /b 0

:sync_overrides
if not exist "%OVERRIDE_DIR%" exit /b 0
if not exist "%VENV_PY%" exit /b 0
set MEMORA_GRAPH_DIR=
for /f "usebackq delims=" %%d in (`"%VENV_PY%" -c "import inspect, pathlib, memora.graph; print(pathlib.Path(inspect.getfile(memora.graph)).resolve().parent)"`) do (
    set MEMORA_GRAPH_DIR=%%d
)
if "!MEMORA_GRAPH_DIR!"=="" exit /b 0
if exist "%OVERRIDE_DIR%\index.html" copy /Y "%OVERRIDE_DIR%\index.html" "!MEMORA_GRAPH_DIR!\index.html" >nul
if exist "%OVERRIDE_DIR%\data.py" copy /Y "%OVERRIDE_DIR%\data.py" "!MEMORA_GRAPH_DIR!\data.py" >nul
if exist "%OVERRIDE_DIR%\server.py" copy /Y "%OVERRIDE_DIR%\server.py" "!MEMORA_GRAPH_DIR!\server.py" >nul
echo Applied memora overrides from %OVERRIDE_DIR%
exit /b 0

:kill_port
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /R /C:":%1 .*LISTENING"') do (
    echo Cleaning listener on port %1: PID %%p
    taskkill /pid %%p /f /t >nul 2>nul
)
exit /b 0
