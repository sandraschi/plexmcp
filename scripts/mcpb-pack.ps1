param(
    [string]$RepoRoot = (Split-Path -Parent $PSScriptRoot)
)
$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

New-Item -ItemType Directory -Force -Path dist | Out-Null
$proj = Get-Content pyproject.toml -Raw
$name = if ($proj -match '(?m)^name = "(.*)"') { $matches[1] } else { Split-Path -Leaf $PWD }
$ver = if ($proj -match '(?m)^version = "(.*)"') { $matches[1] } else { "0.1.0" }

$pkgName = $name -replace '_', '-'
$bundleName = "${pkgName}-v${ver}.mcpb"

Write-Host "=== MCPB Pack: ${bundleName} ===" -ForegroundColor Cyan

# Pack from repo root (manifest.json is at root, .mcpbignore controls excludes)
npx --yes @anthropic-ai/mcpb pack "$RepoRoot" "$RepoRoot\dist\$bundleName"

if ($LASTEXITCODE -ne 0) { throw "mcpb pack failed with exit code $LASTEXITCODE" }

Write-Host "Bundle: $RepoRoot\dist\$bundleName" -ForegroundColor Green
$size = (Get-Item "$RepoRoot\dist\$bundleName").Length / 1MB
Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Green
