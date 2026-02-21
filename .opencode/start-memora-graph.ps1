# Memora Graph Server - PowerShell Starter (modo persistente)

$rootDir = Split-Path -Parent $PSScriptRoot
$dbPath = Join-Path $rootDir ".opencode\memory\memoria.db"
$pidFile = Join-Path $rootDir ".opencode\memora-graph.pid"
$logFile = Join-Path $rootDir ".opencode\memora-graph.log"
$venvMemora = Join-Path $rootDir ".opencode\.venv-memora\Scripts\memora-server.exe"

if (Test-Path $venvMemora) {
    $memoraCmd = $venvMemora
} elseif (Get-Command memora-server -ErrorAction SilentlyContinue) {
    $memoraCmd = "memora-server"
} else {
    Write-Host "Memora runtime nao encontrado." -ForegroundColor Red
    Write-Host "Instale e tente novamente." -ForegroundColor Yellow
    exit 1
}

$env:MEMORA_DB_PATH = $dbPath
$env:MEMORA_ALLOW_ANY_TAG = "1"
$env:MEMORA_GRAPH_PORT = "8765"

Write-Host "Starting Memora Graph Server..." -ForegroundColor Cyan
Write-Host "Graph UI: http://127.0.0.1:8765/graph" -ForegroundColor Green
Write-Host "MCP SSE: http://127.0.0.1:8000/sse" -ForegroundColor Green
Write-Host ""

if (Test-Path $pidFile) {
    $oldPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($oldPid -and (Get-Process -Id $oldPid -ErrorAction SilentlyContinue)) {
        Write-Host "Memora Graph ja esta em execucao (PID $oldPid)." -ForegroundColor Yellow
        exit 0
    }
}

$proc = Start-Process -FilePath $memoraCmd `
    -ArgumentList "--transport", "sse", "--host", "127.0.0.1", "--port", "8000" `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError $logFile `
    -PassThru

$proc.Id | Out-File -FilePath $pidFile -Encoding ascii

$ready = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8765/graph" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # keep retrying
    }
}

if ($ready) {
    Write-Host "Graph server started successfully! (PID $($proc.Id))" -ForegroundColor Green
    Write-Host "Log: $logFile" -ForegroundColor Gray
    Write-Host "To stop: Stop-Process -Id $($proc.Id)" -ForegroundColor Gray
} else {
    Write-Host "Falha ao validar Graph UI. Verifique o log: $logFile" -ForegroundColor Red
    Stop-Process -Id $proc.Id -ErrorAction SilentlyContinue
    Remove-Item $pidFile -ErrorAction SilentlyContinue
    exit 1
}
