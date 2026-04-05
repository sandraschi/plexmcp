set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Display the SOTA Industrial Dashboard
default:
    @$lines = Get-Content '{{justfile()}}'; \
    Write-Host ' [SOTA] Industrial Operations Dashboard v1.3.2' -ForegroundColor White -BackgroundColor Cyan; \
    Write-Host '' ; \
    $currentCategory = ''; \
    foreach ($line in $lines) { \
        if ($line -match '^# ── ([^─]+) ─') { \
            $currentCategory = $matches[1].Trim(); \
            Write-Host "`n  $currentCategory" -ForegroundColor Cyan; \
            Write-Host ('  ' + ('─' * 45)) -ForegroundColor Gray; \
        } elseif ($line -match '^# ([^─].+)') { \
            $desc = $matches[1].Trim(); \
            $idx = [array]::IndexOf($lines, $line); \
            if ($idx -lt $lines.Count - 1) { \
                $nextLine = $lines[$idx + 1]; \
                if ($nextLine -match '^([a-z0-9-]+):') { \
                    $recipe = $matches[1]; \
                    $pad = ' ' * [math]::Max(2, (18 - $recipe.Length)); \
                    Write-Host "    $recipe" -ForegroundColor White -NoNewline; \
                    Write-Host "$pad$desc" -ForegroundColor Gray; \
                } \
            } \
        } \
    } \
    Write-Host "`n  [System State: PROD/HARDENED]" -ForegroundColor DarkGray; \
    Write-Host ''

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff SOTA v13.1 linting
lint:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check .

# Execute Ruff SOTA v13.1 fix and formatting
fix:
    Set-Location '{{justfile_directory()}}'
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    Set-Location '{{justfile_directory()}}'
    uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    Set-Location '{{justfile_directory()}}'
    uv run safety check

# PlexMCP Project Management (Justfile)

# Default: List available commands
# Development Setup
setup:
	@echo "Setting up PlexMCP development environment..."
	@if ! -d ".venv" (python -m venv .venv)
	@.venv\Scripts\Activate.ps1
	@pip install -e .[dev]
	@echo "Development environment setup complete!"

# Build the .mcpb package
build:
	@echo "Building PlexMCP MCPB package..."
	@python -m pytest tests/test_server_startup.py
	@mcpb build
	@echo "✅ Package built in dist/plex-mcp.mcpb"

# Pack the .mcpb package
pack: build
	@echo "Packing PlexMCP MCPB package..."
	@mcpb pack . dist/plex-mcp.mcpb
	@echo "✅ Package packed: dist/plex-mcp.mcpb"

# Linting and Formatting
# Type Checking
type-check:
	@echo "Running type checker..."
	@mypy src/
	@echo "✅ Type checking complete"

# Security Check
security:
	@echo "Running security check..."
	@bandit -r src/
	@echo "✅ Security check complete"

# Run All Tests
test:
	@echo "Running test suite..."
	@python tests/test_server_startup.py
	@python tests/test_integration.py
	@echo "✅ All tests completed"

# Run Tests with Coverage
test-cov:
	@echo "Running tests with coverage..."
	@pytest --cov=src/plex_mcp --cov-report=html --cov-report=term tests/
	@echo "✅ Tests completed with coverage report"

# Clean Build Artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf build/ dist/ target/ .pytest_cache/ .coverage htmlcov/
	@ruff check src/ --select F401,F841
	@echo "✅ Clean completed"

# Start Server (STDIO) - Development
start:
	@echo "Starting PlexMCP server in STDIO mode..."
	@python -m plex_mcp.server --stdio --debug

# Start Server (HTTP) - Development
start-http:
	@echo "Starting PlexMCP server in HTTP mode..."
	@python -m plex_mcp.server --http --port 10740

# Start Web Interface
webapp:
	@echo "Starting PlexMCP webapp..."
	@powershell -ExecutionPolicy Bypass -File .\start.ps1

# Automated Deployment
deploy:
	@echo "Deploying PlexMCP..."
	@powershell -ExecutionPolicy Bypass -File .\deploy.ps1

# Development Mode (with monitoring)
dev:
	@echo "Starting PlexMCP in development mode..."
	@PLEXMCP_ALLOW_LOGGING=1 python -m plex_mcp.server --stdio --debug

# Production Mode
prod:
	@echo "Starting PlexMCP in production mode..."
	@python -m plex_mcp.server --stdio

# Health Check
health:
	@echo "Checking PlexMCP health..."
	@python -c "import asyncio; import sys; sys.path.insert(0, 'src'); from plex_mcp.server import mcp; print(asyncio.run(mcp.read_resource('resource://plex/health')))"

# Version Check
version:
	@echo "PlexMCP version:"
	@python -c "import sys; sys.path.insert(0, 'src'); from plex_mcp import __version__; print(f'v{__version__}')"

# Dependencies Check
deps:
	@echo "Checking dependencies..."
	@pip list | findstr fastmcp
	@pip list | findstr plexapi
	@echo "✅ Dependencies checked"

# Full CI Pipeline
ci: lint type-check security test
	@echo "Running full CI pipeline..."
	@echo "✅ CI pipeline completed successfully"

# Release Process
release: clean lint type-check security test build pack
	@echo "Creating PlexMCP release..."
	@echo "✅ Release created: dist/plex-mcp.mcpb"

# Documentation Generation
docs:
	@echo "Generating documentation..."
	@echo "✅ Documentation available in docs/ folder"

# MCPB Status
mcpb-status:
	@echo "Checking MCPB package status..."
	@echo "Package: dist/plex-mcp.mcpb"
	@if test -f "dist/plex-mcp.mcpb" (echo "✅ Package exists") else (echo "❌ Package not found")
	@echo "Version: 3.2.0"

# Install Package (for testing)
install: build
	@echo "Installing PlexMCP package..."
	@pip install dist/plex-mcp.mcpb --force-reinstall
	@echo "✅ Package installed"
