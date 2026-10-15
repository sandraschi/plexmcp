#Requires -Version 5.1
# Thin shim — the canonical pack pipeline lives in the fleet hub so fixes
# reach every repo at once (see mcp-central-docs/scripts/fleet-mcpb-pack.ps1).
param([string]$RepoRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = "Stop"
$hub = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) "mcp-central-docs\scripts\fleet-mcpb-pack.ps1"
if (-not (Test-Path $hub)) { $hub = "D:\Dev\repos\mcp-central-docs\scripts\fleet-mcpb-pack.ps1" }
if (-not (Test-Path $hub)) { throw "Fleet hub script not found: $hub. Clone mcp-central-docs next to this repo (D:\Dev\repos layout) and retry." }
& $hub -RepoRoot $RepoRoot
