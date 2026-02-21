param()
$ErrorActionPreference = 'Continue'

$venvPy     = 'g:\projetos\docs-copy\.opencode\.venv-memora\Scripts\python.exe'
$memoraExe  = 'g:\projetos\docs-copy\.opencode\.venv-memora\Scripts\memora-server.exe'
$overrideDir = 'g:\projetos\docs-copy\.opencode\memora-overrides\graph'
$logFile    = 'g:\projetos\docs-copy\.opencode\memora-graph.log'
$pidFile    = 'g:\projetos\docs-copy\.opencode\memora-graph.pid'

# 1. Descobrir diretório do pacote memora.graph
$graphDir = & $venvPy -c "import inspect, pathlib, memora.graph; print(pathlib.Path(inspect.getfile(memora.graph)).resolve().parent)" 2>&1
if (-not $graphDir -or $graphDir -like '*Error*') {
    Write-Host "ERRO: Nao foi possivel localizar memora.graph - $graphDir"
    exit 1
}
Write-Host "Package dir: $graphDir"

# 2. Sincronizar overrides
foreach ($f in @('index.html', 'data.py', 'server.py')) {
    $src = Join-Path $overrideDir $f
    $dst = Join-Path $graphDir $f
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "Copiado: $f -> $dst"
    }
}
Write-Host "Sync concluido."

# 3. Iniciar servidor em background
Write-Host "Iniciando memora-server..."
$proc = Start-Process -FilePath $memoraExe `
    -ArgumentList @('--transport', 'sse', '--host', '127.0.0.1', '--port', '8000') `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError $logFile `
    -PassThru `
    -WindowStyle Hidden

if (-not $proc) {
    Write-Host "ERRO: Falha ao iniciar processo."
    exit 1
}

$proc.Id | Out-File $pidFile -Encoding ascii
Write-Host "Servidor iniciado com PID $($proc.Id)"

# 4. Aguardar até 20s para o servidor responder
Write-Host "Aguardando servidor em 127.0.0.1:8765..."
$ready = $false
for ($i = 0; $i -lt 10; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8765/causal-observer' -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Write-Host "  tentativa $($i+1)..."
}

if ($ready) {
    Write-Host ""
    Write-Host "Servidor pronto!"
    Write-Host "  Causal Observer : http://127.0.0.1:8765/causal-observer"
    Write-Host "  Graph classico  : http://127.0.0.1:8765/graph"
    Write-Host "  PID             : $($proc.Id)"
} else {
    Write-Host "AVISO: Servidor nao respondeu a tempo. Verifique o log: $logFile"
}
