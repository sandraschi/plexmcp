# Usage Guide

This guide provides examples of how to use PlexMCP portmanteau tools for common tasks.

## Portmanteau Tool Architecture

PlexMCP uses **15 portmanteau tools** that consolidate related operations. Each tool uses an `operation` parameter to specify the action.

### Tool Structure

All portmanteau tools follow this pattern:
```python
tool_name(operation="operation_name", ...other_parameters)
```

## Basic Usage

### Starting the Server

```powershell
# Start the server with default settings (STDIO mode for Claude Desktop)
python -m plex_mcp.server

# Start with HTTP mode
python -m plex_mcp.server --http --host 0.0.0.0 --port 8000

# Enable debug mode
python -m plex_mcp.server --debug
```

### Using Portmanteau Tools

All tools are accessed through Claude Desktop or MCP clients. Examples show the tool call format:

```python
# Get all libraries
plex_library(operation="list")

# Search for media
plex_media(operation="search", query="The Matrix")

# Get library details
plex_library(operation="get", library_id="1")
```

## Common Tasks

### 1. Play Media on a Client

```python
# List available clients
plex_streaming(operation="list_clients")

# Play a specific media item on a client
plex_streaming(
    operation="play",
    client_id="abc123",
    media_key="12345"
)

# Pause playback
plex_streaming(operation="pause", client_id="abc123")

# Seek to specific time (in milliseconds)
plex_streaming(operation="seek", client_id="abc123", seek_to=60000)
```

### 2. Create a Playlist

```python
# Create a new playlist
plex_playlist(
    operation="create",
    title="My Favorites",
    items=["12345", "67890"],  # List of media IDs
    description="My favorite movies"
)

# Add items to an existing playlist
plex_playlist(
    operation="add_items",
    playlist_id="playlist123",
    items=["54321"]
)

# Get playlist analytics
plex_playlist(operation="get_analytics", playlist_id="playlist123")
```

### 3. Control Playback

```python
# List active sessions
plex_streaming(operation="list_sessions")

# Pause playback
plex_streaming(operation="pause", client_id="abc123")

# Skip to next item
plex_streaming(operation="skip_next", client_id="abc123")

# Generic control with action
plex_streaming(
    operation="control",
    client_id="abc123",
    action="play",
    media_key="12345"
)
```

### 4. Library Management

```python
# List all libraries
plex_library(operation="list")

# Get library details
plex_library(operation="get", library_id="1")

# Refresh a library
plex_library(operation="refresh", library_id="1")

# Scan for new files
plex_library(operation="scan", library_id="1", force=True)

# Get recently added items
plex_media(operation="get_recent", library_id="1", limit=10)
```

## Advanced Usage

### WebSocket Events

Plex MCP provides real-time updates via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data);
    
    // Handle different event types
    switch(data.event) {
        case 'play':
            console.log('Playback started:', data.data);
            break;
        case 'pause':
            console.log('Playback paused');
            break;
        case 'media.scan':
            console.log('Library scan event');
            break;
    }
};
```

### Custom Middleware

You can extend Plex MCP with custom middleware:

```python
from fastapi import Request, Response

async def custom_middleware(request: Request, call_next):
    # Do something before the request
    print(f"Request: {request.method} {request.url}")
    
    # Process the request
    response = await call_next(request)
    
    # Do something after the request
    response.headers["X-Custom-Header"] = "PlexMCP"
    return response

# Add middleware when creating the app
app.add_middleware(BaseHTTPMiddleware, dispatch=custom_middleware)
```

## Command Line Interface

Plex MCP comes with a command-line interface:

```powershell
# Show help
plexmcp --help

# List libraries
plexmcp libraries list

# Search for media
plexmcp search "The Matrix"

# Control playback
plexmcp play --client "Living Room TV" --media 12345
plexmcp pause --client "Living Room TV"
plexmcp stop --client "Living Room TV"
```

## Integration Examples

### Home Assistant

```yaml
# configuration.yaml
rest_command:
  plex_play_media:
    url: http://localhost:8000/api/v1/playback/play
    method: POST
    headers:
      Authorization: !secret plex_token
      Content-Type: application/json
    payload: >
      {
        "client_name": "{{ client_name }}",
        "media_id": "{{ media_id }}"
      }
```

### Node-RED

Use the HTTP Request node to interact with the Plex MCP API:

```
[{"id":"node-id","type":"http request","z":"flow-id","name":"Plex MCP","method":"POST","ret":"obj","paytoqs":"ignore","url":"http://localhost:8000/api/v1/playback/play","tls":"","persist":false,"proxy":"","authType":"bearer","x":480,"y":120,"wires":[["output-node-id"]]}]
```
