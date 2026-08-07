set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# PlexMCP Project Management (Justfile)

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# Print `project.version` from `pyproject.toml` (source of truth; use when syncing README badges)
version:
	@uv run python -c "import pathlib, tomllib; p = pathlib.Path('pyproject.toml'); print(tomllib.loads(p.read_text(encoding='utf-8'))['project']['version'])"

# --- Basic Workflow ---

# Synchronize deps, pre-commit hooks, and webapp frontend
bootstrap:
    uv sync --extra dev --group dev
    uv run pre-commit install
    Set-Location webapp/frontend; npm ci; if ($LASTEXITCODE -ne 0) { npm install }
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green

# Setup development environment
install: bootstrap

# Start Server (STDIO)
start:
	uv run plex-mcp-advanced

# Start Web Interface
webapp:
	@powershell -ExecutionPolicy Bypass -File webapp/start.ps1

# --- Quality Gates ---

# Lint and check all files (Python + JS/TS + Security)
lint:
	@echo "--- Checking Python (Ruff) ---"
	uv run ruff check .
	@echo "--- Checking JS/TS (Biome) ---"
	cd webapp/frontend && npx @biomejs/biome check .
	@echo "--- Checking Security (Semgrep) ---"
	@just _semgrep-if-supported

# --- On Windows Semgrep s installed CLI is often broken in the same ways as in pre-commit CI runs it on Ubuntu ---
[windows]
_semgrep-if-supported:
	@echo "Skipping local Semgrep on Windows; use CI or WSL, or install Semgrep and run: semgrep scan --config auto ."

[unix]
_semgrep-if-supported:
	semgrep scan --config auto .

# Format all files
fmt:
	uv run ruff format .
	cd webapp/frontend && npx @biomejs/biome format --write .

# Automated fix (Ruff + Biome)
fix:
	uv run ruff check . --fix
	uv run ruff format .
	cd webapp/frontend && npx @biomejs/biome check --write .

# Run Tests
test:
	@uv run pytest --cov=src/plex_mcp tests/

# Playwright smoke (Next dev is started by Playwright; run `npm ci` in webapp/frontend first)
e2e:
	cd webapp/frontend; npm run test:e2e

# Integration Tests (requires PLEX_TOKEN and PLEX_URL)
test-integration:
	@uv run pytest tests/test_integration_real_plex.py -v

# Serve docs locally (via docsify or similar)
docs-serve:
	@echo "Open docs/README.md in your editor or run: npx docsify-cli serve ./docs"

# --- Build & CI ---

# Run full CI suite locally
ci: lint test

# Build the .mcpb package
build:
	@powershell -ExecutionPolicy Bypass -File webapp/start.ps1 -BuildOnly
	@echo "Package built in dist/plex-mcp.mcpb"

# Cleanup
clean:
	@powershell -Command "Remove-Item -Recurse -Force .pytest_cache, .ruff_cache, dist, build, htmlcov -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Directory -Filter __pycache__ -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"

# --- Native  Tauri ---

# --- Build embedded Python backend  native resources ---
build-sidecar:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File '{{justfile_directory()}}\native\build-sidecar.ps1'

# Primary end-user deliverable: Next static export + embedded backend + NSIS
build-native install-desktop:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

build-native-debug:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

# --- RAG  LanceDB metadata sync ---

# Sync Plex metadata into LanceDB (CPU)
rag-sync:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-sync.ps1

# Sync Plex metadata into LanceDB on GPU (after rag-gpu-install)
rag-gpu-sync:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-gpu-sync.ps1

# One-time: install fastembed-gpu + onnxruntime-gpu + NVIDIA CUDA 12 runtimes (~1.5 GB)
rag-gpu-install:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-gpu-install.ps1

# Revert to CPU onnxruntime stack
rag-cpu-install:
    @powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/just/rag-cpu-install.ps1

# Bootstrap: install dev deps + pre-commit hook
