# Plex metadata RAG sync on CPU - venv python (not uv run while GPU mode active).
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot
$py = & (Join-Path $PSScriptRoot "rag-python.ps1")
& $py scripts/plex_rag_sync.py @args
exit $LASTEXITCODE
