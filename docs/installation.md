# Installation Guide

This guide will walk you through installing and setting up Plex MCP on your system.

## Prerequisites

- Python 3.8 or higher
- Plex Media Server (local or remote)
- Plex authentication token
- Git (for development installation)

## Installation Methods

### 1. Using pip (Recommended)

```powershell
# Install from PyPI
pip install plex-mcp
```

### 2. From Source

```powershell
# Clone the repository
git clone https://github.com/yourusername/plexmcp.git
cd plexmcp

# Install in development mode
pip install -e .
```

### 3. Docker (Coming Soon)

```powershell
docker pull yourusername/plexmcp:latest
```

## Configuration

Create a `.env` file in the project root with the following variables:

```ini
# Required
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your_plex_token_here

# Optional
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## Verifying the Installation

```powershell
# Check the installed version
plexmcp --version

# Run the server
plexmcp run
```

## Upgrading

```powershell
# Upgrade using pip
pip install --upgrade plex-mcp
```

## Uninstalling

```powershell
# Uninstall the package
pip uninstall plex-mcp
```

## Troubleshooting

If you encounter any issues during installation, please refer to the [Troubleshooting Guide](./troubleshooting.md).
