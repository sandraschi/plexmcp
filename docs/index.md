# Plex MCP Documentation

Welcome to the Plex MCP (Media Control Protocol) documentation. This project provides a powerful interface for controlling and automating Plex Media Server through a standardized MCP (Model Control Protocol) interface.

## Overview

Plex MCP is a bridge between Plex Media Server and MCP-compatible clients, enabling advanced automation and control of your Plex media library. It provides a RESTful API and MCP-compliant interface for managing your Plex server programmatically.

## Features

- **Media Management**: Browse and search your Plex library
- **Playback Control**: Control media playback on Plex clients
- **Playlist Management**: Create and manage playlists
- **User Management**: Manage Plex users and permissions
- **Automation**: Automate common Plex tasks
- **Web Interface**: Built-in web interface for easy management

## Getting Started

1. [Installation Guide](./installation.md)
2. [Configuration](./configuration.md)
3. [Usage Examples](./usage.md)
4. [API Reference](./api/)
5. [Troubleshooting](./troubleshooting.md)
6. [Development](./development.md)

## Quick Start

```python
from plexapi.server import PlexServer

# Connect to Plex server
plex = PlexServer('http://localhost:32400', 'YOUR_PLEX_TOKEN')

# List all libraries
for library in plex.library.sections():
    print(f"Library: {library.title}")
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
