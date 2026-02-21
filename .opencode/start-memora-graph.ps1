# Memora Graph Server - PowerShell Starter (modo persistente)

$rootDir = Split-Path -Parent $PSScriptRoot
$dbPath = Join-Path $rootDir ".opencode\memory\memoria.db"
$pidFile = Join-Path $rootDir ".opencode\memora-graph.pid"
$logFile = Join-Path $rootDir ".opencode\memora-graph.log"
$venvMemora = Join-Path $rootDir ".opencode\.venv-memora\Scripts\memora-server.exe"
$venvPython = Join-Path $rootDir ".opencode\.venv-memora\Scripts\python.exe"
$overrideDir = Join-Path $rootDir ".opencode\memora-overrides\graph"

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
$graphPort = 8765
$mcpPort = 8000

function Stop-PidSafe {
    param([int]$Pid)
    if (-not $Pid) { return }
    $proc = Get-Process -Id $Pid -ErrorAction SilentlyContinue
    if (-not $proc) { return }
    try { Stop-Process -Id $Pid -ErrorAction SilentlyContinue } catch {}
    Start-Sleep -Seconds 1
    $proc = Get-Process -Id $Pid -ErrorAction SilentlyContinue
    if ($proc) {
        try { Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue } catch {}
    }
}

function Get-ListenerPids {
    param([int]$Port)
    $pids = @()
    try {
        $items = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction Stop
        $pids += $items | Select-Object -ExpandProperty OwningProcess -Unique
    } catch {
        # Fallback for systems without Get-NetTCPConnection permissions/modules
        $netstat = netstat -ano | Select-String ":$Port"
        foreach ($line in $netstat) {
            $parts = ($line.ToString().Trim() -replace "\s+", " ").Split(" ")
            if ($parts.Length -ge 5) {
                $pid = 0
                [void][int]::TryParse($parts[-1], [ref]$pid)
                if ($pid -gt 0) { $pids += $pid }
            }
        }
    }
    return $pids | Sort-Object -Unique
}

function Cleanup-ExistingInstance {
    if (Test-Path $pidFile) {
        $oldPidRaw = Get-Content $pidFile -ErrorAction SilentlyContinue
        $oldPid = 0
        [void][int]::TryParse(($oldPidRaw -join "").Trim(), [ref]$oldPid)
        if ($oldPid -gt 0) {
            Write-Host "Stopping existing Memora process from PID file: $oldPid" -ForegroundColor Yellow
            Stop-PidSafe -Pid $oldPid
        }
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }

    foreach ($port in @($graphPort, $mcpPort)) {
        $pids = Get-ListenerPids -Port $port
        if ($pids.Count -gt 0) {
            Write-Host "Cleaning listeners on port $port: $($pids -join ', ')" -ForegroundColor Yellow
            foreach ($pid in $pids) {
                Stop-PidSafe -Pid $pid
            }
        }
    }
}

function Sync-MemoraOverrides {
    if (-not (Test-Path $overrideDir)) { return }
    if (-not (Test-Path $venvPython)) { return }

    $graphDir = ""
    try {
        $graphDir = & $venvPython -c "import inspect, pathlib, memora.graph; print(pathlib.Path(inspect.getfile(memora.graph)).resolve().parent)"
    } catch {
        $graphDir = ""
    }
    if (-not $graphDir) { return }
    if (-not (Test-Path $graphDir)) { return }

    $synced = $false
    foreach ($file in @("index.html", "data.py", "server.py")) {
        $src = Join-Path $overrideDir $file
        if (Test-Path $src) {
            Copy-Item -Force $src (Join-Path $graphDir $file)
            $synced = $true
        }
    }
    if ($synced) {
        Write-Host "Applied memora overrides from $overrideDir" -ForegroundColor Gray
    }
}

Write-Host "Starting Memora Graph Server..." -ForegroundColor Cyan
Write-Host "Graph UI: http://127.0.0.1:$graphPort/graph" -ForegroundColor Green
Write-Host "MCP SSE: http://127.0.0.1:$mcpPort/sse" -ForegroundColor Green
Write-Host ""

Sync-MemoraOverrides
Cleanup-ExistingInstance

$proc = Start-Process -FilePath $memoraCmd `
    -ArgumentList "--transport", "sse", "--host", "127.0.0.1", "--port", "$mcpPort" `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError $logFile `
    -PassThru

$proc.Id | Out-File -FilePath $pidFile -Encoding ascii

$ready = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 2
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$graphPort/graph" -UseBasicParsing -TimeoutSec 5
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
