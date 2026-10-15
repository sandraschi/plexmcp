#Requires -Version 5.1
# Forwarder — the single pack entry point is scripts/mcpb-pack.ps1 (fleet
# shim with local fallback). Kept so existing docs and CI references to
# mcpb/pack.ps1 keep working without vendoring a second pipeline copy.
param([string]$RepoRoot = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = "Stop"
& (Join-Path $RepoRoot "scripts\mcpb-pack.ps1") -RepoRoot $RepoRoot
