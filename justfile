set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# PlexMCP Project Management (Justfile)

# Default: List available commands
default:
	@just --list

# Print `project.version` from `pyproject.toml` (source of truth; use when syncing README badges)
version:
	@uv run python -c "import pathlib, tomllib; p = pathlib.Path('pyproject.toml'); print(tomllib.loads(p.read_text(encoding='utf-8'))['project']['version'])"

# --- Basic Workflow ---

# Setup development environment
install:
	uv sync
	pre-commit install

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
	ruff check .
	@echo "--- Checking JS/TS (Biome) ---"
	cd webapp/frontend && npx @biomejs/biome check .
	@echo "--- Checking Security (Semgrep) ---"
	@just _semgrep-if-supported

# On Windows, Semgrep’s installed CLI is often broken in the same ways as in pre-commit; CI runs it on Ubuntu.
[windows]
_semgrep-if-supported:
	@echo "Skipping local Semgrep on Windows; use CI or WSL, or install Semgrep and run: semgrep scan --config auto ."

[unix]
_semgrep-if-supported:
	semgrep scan --config auto .

# Format all files
fmt:
	ruff format .
	cd webapp/frontend && npx @biomejs/biome format --write .

# Automated fix (Ruff + Biome)
fix:
	ruff check . --fix
	ruff format .
	cd webapp/frontend && npx @biomejs/biome check --write .

# Run Tests
test:
	@pytest --cov=src/plex_mcp tests/

# Playwright smoke (Next dev is started by Playwright; run `npm ci` in webapp/frontend first)
e2e:
	cd webapp/frontend; npm run test:e2e

# Integration Tests (requires PLEX_TOKEN and PLEX_URL)
test-integration:
	@pytest tests/test_integration_real_plex.py -v

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
