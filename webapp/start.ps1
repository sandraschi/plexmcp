# Webapp Start - Standardized SOTA (Auto-Repaired V2.5)
$WebPort = 10741
$BackendPort = 10740
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 0. Ensure we run npm from the dir that has package.json (webapp or webapp/frontend)
$NpmRoot = $PSScriptRoot
if (-not (Test-Path (Join-Path $NpmRoot "package.json"))) {
    $NpmRoot = Join-Path $PSScriptRoot "frontend"
}
if (-not (Test-Path (Join-Path $NpmRoot "package.json"))) {
    Write-Host "ERROR: package.json not found in $PSScriptRoot or $PSScriptRoot\frontend. Run this script from plex-mcp\webapp (e.g. use webapp\start.bat)." -ForegroundColor Red
    exit 1
}

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup (npm from dir that has package.json)
Set-Location $NpmRoot
if (-not (Test-Path "node_modules")) { npm install }

# 3. Start the Python backend (FastAPI with /api/* and MCP at /mcp)
Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan

$BackendDir = Join-Path $ProjectRoot "webapp\backend"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$backendCmd = "`$env:PYTHONPATH = '$ProjectRoot\src;$BackendDir'; Set-Location '$BackendDir'; & '$VenvPython' -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --log-level info"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Run server (Vite dev) from same npm root
Set-Location $NpmRoot
Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
npm run dev -- --port $WebPort

