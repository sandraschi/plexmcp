# Run PlexMCP for Cursor IDE (stdio). Sets PYTHONPATH so package need not be installed.
# Cursor runs this with cwd = workspace root (folder containing .cursor).
$ErrorActionPreference = "Stop"
$repoRoot = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { Get-Location }
$srcPath = Join-Path $repoRoot "src"
if (-not (Test-Path $srcPath)) {
    Write-Error "PlexMCP: src not found at $srcPath"
    exit 1
}

# Load PLEX_TOKEN from webapp/backend/.env if not already set
$envFile = Join-Path $repoRoot "webapp" "backend" ".env"
if ((Test-Path $envFile) -and -not $env:PLEX_TOKEN) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^PLEX_TOKEN\s*=\s*(.+)$') {
            $env:PLEX_TOKEN = $matches[1].Trim('"').Trim("'").Trim()
        }
        if ($_ -match '^PLEX_URL\s*=\s*(.+)$') {
            $env:PLEX_URL = $matches[1].Trim('"').Trim("'").Trim()
        }
    }
}

# Check that PLEX_TOKEN is set
if (-not $env:PLEX_TOKEN) {
    Write-Error "PlexMCP: PLEX_TOKEN not set. Set it in webapp/backend/.env or as env var."
    exit 1
}

$env:PYTHONPATH = $srcPath
Set-Location $repoRoot
python -m plex_mcp
