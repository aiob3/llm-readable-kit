# ============================================
# Memora Graph Server - PowerShell Starter
# Executar como administrador se necessário
# ============================================

$env:MEMORA_DB_PATH = "G:\projetos\docs-copy\.opencode\memory\memoria.db"
$env:MEMORA_ALLOW_ANY_TAG = "1"
$env:MEMORA_GRAPH_PORT = "8765"

$pythonPath = "C:\Users\papa\AppData\Local\Programs\Python\Python313\python.exe"

Write-Host "Starting Memora Graph Server..." -ForegroundColor Cyan
Write-Host "Graph UI: http://localhost:8765/graph" -ForegroundColor Green
Write-Host ""

# Start the server in background
Start-Process -FilePath $pythonPath -ArgumentList "-m", "memora", "--graph-port", "8765" -NoNewWindow -PassThru

Start-Sleep -Seconds 3

# Verify it's running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8765/graph" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "Graph server started successfully!" -ForegroundColor Green
        Write-Host "Access: http://localhost:8765/graph" -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: Could not verify server startup. It may still be initializing." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit (server will continue running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
