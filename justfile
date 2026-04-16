# PlexMCP Project Management (Justfile)

# Default: List available commands
default:
	@just --list

# Build the .mcpb package
build:
	@powershell -ExecutionPolicy Bypass -File webapp/start.ps1 -BuildOnly
	@echo "Package built in dist/plex-mcp.mcpb"

# Linting and Formatting
lint:
	@ruff check . --fix
	@ruff format .

# Run Tests
test:
	@pytest --cov=src/plex_mcp tests/

# Start Server (STDIO)
start:
	@python -m plex_mcp.server

# Start Web Interface
webapp:
	@powershell -ExecutionPolicy Bypass -File webapp/start.ps1
