# PlexMCP Webapp Start - Reservoir ports 10740 (backend), 10741 (frontend)
# Run: powershell -ExecutionPolicy Bypass -File start.ps1

$BackendPort = 10740
$FrontendPort = 10741
$WebappRoot = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $WebappRoot
$SrcPath = Join-Path $ProjectRoot "src"

# 1. Clear ports (kill-port preferred)
$frontendDir = Join-Path $WebappRoot "frontend"
Set-Location $frontendDir
try {
    npx --yes kill-port $BackendPort $FrontendPort 2>$null
} catch { }
Set-Location $WebappRoot
Start-Sleep -Seconds 1

# 2. Env for backend
$env:PYTHONPATH = $SrcPath
$env:PORT = $BackendPort
$env:CORS_ORIGINS = "http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort"

# 3. Start backend
if (-not (Test-Path $SrcPath)) {
    Write-Host "[ERROR] Source path not found: $SrcPath" -ForegroundColor Red
    exit 1
}
Write-Host "[INFO] Backend http://localhost:$BackendPort  Frontend http://localhost:$FrontendPort" -ForegroundColor Green
$backendDir = Join-Path $WebappRoot "backend"
$backendCmd = "Set-Location '$backendDir'; `$env:PYTHONPATH='$SrcPath'; `$env:PORT='$BackendPort'; `$env:CORS_ORIGINS='http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BackendPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 2

# 4. Start frontend
$apiUrl = "http://127.0.0.1:$BackendPort"
$appUrl = "http://127.0.0.1:$FrontendPort"
$frontendCmd = "Set-Location '$frontendDir'; `$env:API_URL='$apiUrl'; `$env:NEXT_PUBLIC_API_URL='$apiUrl'; `$env:NEXT_PUBLIC_APP_URL='$appUrl'; npx next dev -p $FrontendPort"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Write-Host "Backend and frontend started. Close their windows to stop."
