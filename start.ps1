# Plex-MCP Start Script (SOTA 2026)
$WebPort = 10741
$BackendPort = 10740
$ProjectRoot = $PSScriptRoot

# 1. Kill any process squatting on the ports (Checking IPv4 and IPv6)
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | 
        Where-Object { $_.OwningProcess -gt 4 } | 
        Select-Object -ExpandProperty OwningProcess -Unique

foreach ($p in $pids) {
    try {
        $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Found squatter '$($proc.Name)' (PID: $p). Terminating..." -ForegroundColor Red
            Stop-Process -Id $p -Force -ErrorAction Stop
        }
    } catch {
        Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray
    }
}

# 2. Setup
$FrontendDir = Join-Path $ProjectRoot "webapp\frontend"
Set-Location $FrontendDir
if (-not (Test-Path "node_modules")) { 
    Write-Host "Installing dependencies in $FrontendDir..." -ForegroundColor Gray
    npm install 
}
Set-Location $ProjectRoot

# 3. Start the Python backend
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$BackendDir = Join-Path $ProjectRoot "webapp\backend"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$backendCmd = "`$env:PYTHONPATH = '$ProjectRoot\src;$BackendDir'; Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --log-level info"

# Start backend in a new window
# Note: Using -NoExit so researchers can see startup errors if any occur
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Wait for backend readiness before starting frontend
$maxRetries = 30
$retryCount = 0
$backendReady = $false
Write-Host "Waiting for backend readiness..." -ForegroundColor Yellow -NoNewline

while (-not $backendReady -and $retryCount -lt $maxRetries) {
    try {
        # Using /health instead of /api/server/status is faster and less prone to component initialization delays
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -Method Get -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $backendReady = $true }
    } catch {
        # Expected until server is up
    }
    if (-not $backendReady) {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
        $retryCount++
    }
}

if ($backendReady) {
    Write-Host " [READY]" -ForegroundColor Green
} else {
    Write-Host " [TIMEOUT]" -ForegroundColor Red
    Write-Host "WARNING: Backend did not respond within $maxRetries seconds. Check the backend window for errors." -ForegroundColor Yellow
}

# 5. Start Next.js frontend
Write-Host "Starting Next.js frontend on port $WebPort ..." -ForegroundColor Green
Set-Location $FrontendDir
npm run dev -- --port $WebPort

