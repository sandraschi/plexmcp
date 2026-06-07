param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$WebPort = 10741
$BackendPort = 10740
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$NpmRoot = Join-Path $PSScriptRoot "frontend"

$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
$FleetStart = Initialize-FleetStartMode @PSBoundParameters
Enter-FleetHeadlessConsole -Headless:$Headless -BackendOnly:$BackendOnly
Stop-FleetPortSquatters -Ports @($WebPort, $BackendPort) -Label "plex-mcp"

if (-not (Assert-FleetPortsAvailable -Ports @($WebPort, $BackendPort) -Label "plex-mcp")) { exit 1 }

Set-Location $ProjectRoot
uv sync --project $ProjectRoot
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: uv sync failed for plex-mcp." -ForegroundColor Red
    exit 1
}

Set-Location $NpmRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Gray
    npm install
}

Write-Host "Starting Python backend on port $BackendPort ..." -ForegroundColor Cyan
$BackendDir = Join-Path $ProjectRoot "webapp\backend"
$backendCmd = "`$env:PYTHONPATH = '$ProjectRoot\src;$BackendDir'; Set-Location '$BackendDir'; uv run --project '$ProjectRoot' python -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Normal", "-Command", $backendCmd

$healthUrl = "http://127.0.0.1:$BackendPort/health"
$attempt = 0
while ($attempt -lt 45) {
    try {
        $null = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        Write-Host "Backend ready at $healthUrl" -ForegroundColor Green
        break
    } catch {
        Start-Sleep -Seconds 2
        $attempt++
    }
}

if (-not $FleetStart.RunFrontend) {
    while ($true) { Start-Sleep -Seconds 60 }
}

if (-not $NoBrowser) {
    $frontendUrl = "http://127.0.0.1:$WebPort/"
    $pollAndOpen = "for (`$i = 0; `$i -lt 120; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
    Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen
}

Write-Host "Starting Next.js frontend on port $WebPort ..." -ForegroundColor Green
npm run dev -- -H 127.0.0.1


