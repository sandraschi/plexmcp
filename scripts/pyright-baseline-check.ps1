#Requires -Version 7.0
<#
.SYNOPSIS
  Pyright ratchet gate: fails only when the type-error count grows past baseline.
.DESCRIPTION
  The repo carries legacy pyright errors (concentrated in services/, tools/,
  api/). A blocking zero-error gate today would red-build main, so this script
  ratchets: it runs pyright with the repo pyrightconfig.json, counts
  severity=error diagnostics, and fails when the count exceeds
  scripts/pyright-baseline.txt. Lower the baseline file whenever a batch of
  errors is fixed (it must equal the current count, never higher).
  Uses `uv run --with pyright` so CI needs no lockfile churn.
#>
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$baselineFile = Join-Path $PSScriptRoot "pyright-baseline.txt"
$baseline = 0
if (Test-Path $baselineFile) {
  $baseline = [int]((Get-Content $baselineFile -Raw).Trim())
}

$uv = $null
foreach ($cand in @("C:\Users\sandr\.local\bin\uv.exe", (Join-Path $env:USERPROFILE ".local\bin\uv.exe"))) {
  if ($cand -and (Test-Path $cand)) { $uv = $cand; break }
}
if (-not $uv) {
  $uv = (Get-Command uv -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source)
}
if (-not $uv) { Write-Error "uv not found (tried local path + PATH) — failing closed." }

$json = & $uv run --with pyright pyright --outputjson 2>$null
if ($LASTEXITCODE -ne 0 -and -not $json) {
  Write-Error "pyright did not run (uv/network issue?) — gate inconclusive, failing closed."
}
$count = 0
try {
  $data = $json | ConvertFrom-Json
  $count = @($data.generalDiagnostics | Where-Object { $_.severity -eq "error" }).Count
} catch {
  Write-Error "Could not parse pyright JSON output — failing closed: $_"
}

Write-Host ("pyright errors: {0} (baseline: {1})" -f $count, $baseline)
if ($count -gt $baseline) {
  Write-Error ("FAIL: {0} errors exceed baseline {1}. Fix new type errors first; lower scripts/pyright-baseline.txt only after real fixes." -f $count, $baseline)
}
if ($count -lt $baseline) {
  Write-Host ("NOTE: count {0} is below baseline {1} — lower scripts/pyright-baseline.txt to {0} in a follow-up commit." -f $count, $baseline)
}
Write-Host "PASS: no new pyright errors."
