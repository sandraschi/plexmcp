Param([switch]$Headless, [switch]$BackendOnly, [switch]$NoBrowser)

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
# ------------------------------

$ScriptRoot = Split-Path -Parent $PSCommandPath
$BackendPort = 10740
$FrontendPort = 10741
$UvExe = "C:\Users\sandr\.local\bin\uv.exe"
$NpmCmd = "C:\Program Files\nodejs\npm.cmd"

Write-Host 'Starting plex-mcp...' -ForegroundColor Cyan

# NOTE (2026-10-12): this launcher used to run `uv run plexmcp` (the stdio MCP
# server), which never served the web backend on :10740. Now starts the real
# backend: uvicorn app.main:app in webapp\backend (fleet-start.config.ps1).

# --- Zombie killer (frees both ports before binding) ---
. "$PSScriptRoot\scripts\FleetStartMode.ps1"
$null = Stop-FleetPortSquatters -Ports @($BackendPort, $FrontendPort) -Label 'plex-mcp'

# Start backend: single FastAPI app on the backend port
$BackendJob = Start-Job -Name "backend" -ScriptBlock {
    param($Root, $Port, $Uv)
    Set-Location (Join-Path $Root 'webapp\backend')
    $env:PYTHONPATH = "$Root\webapp\backend;$Root\src"
    $env:WEB_PORT = "$Port"
    & $Uv run uvicorn app.main:app --host 127.0.0.1 --port $Port
} -ArgumentList $ScriptRoot, $BackendPort, $UvExe

# Readiness probe (fail fast with job output instead of silent fallthrough)
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) { Write-Host "Backend ready on port $BackendPort" -ForegroundColor Green; $ready = $true; break }
    } catch {}
    if ($BackendJob.State -eq 'Failed') { break }
    Start-Sleep 1
}
if (-not $ready) {
    Write-Host "Backend did not answer /health in 60s. Job output:" -ForegroundColor Red
    Receive-Job -Job $BackendJob -ErrorAction SilentlyContinue
    Stop-Job -Job $BackendJob -ErrorAction SilentlyContinue
    exit 1
}

if ($BackendOnly) { return }

# Start frontend (Next.js dev server hardcodes -p 10741, own window)
Start-Process cmd.exe -ArgumentList @('/k', "`"$NpmCmd`" run dev") -WorkingDirectory (Join-Path $ScriptRoot 'webapp\frontend')
if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$FrontendPort/" }
