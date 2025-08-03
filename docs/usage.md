# Usage Guide

This guide provides examples of how to use Plex MCP for common tasks.

## Basic Usage

### Starting the Server

```powershell
# Start the server with default settings
plexmcp run

# Start with custom host and port
plexmcp run --host 0.0.0.0 --port 8000

# Enable debug mode
plexmcp run --debug
```

### Using the Python Client

```python
from plexmcp import PlexMCPClient

# Initialize client
client = PlexMCPClient(base_url="http://localhost:8000")

# Get all libraries
libraries = client.get_libraries()
for lib in libraries:
    print(f"Library: {lib.title}")

# Search for media
results = client.search_media("The Matrix")
for item in results:
    print(f"Found: {item.title} ({item.year})")
```

## Common Tasks

### 1. Play Media on a Client

```python
# Play a specific media item on a client
client.play_media(
    client_name="Living Room TV",
    media_id="12345"
)

# Play a specific media URL
client.play_media(
    client_name="Living Room TV",
    media_url="plex://movie/12345"
)
```

### 2. Create a Playlist

```python
# Create a new playlist
playlist = client.create_playlist(
    title="My Favorites",
    items=["12345", "67890"],  # List of media IDs
    description="My favorite movies"
)

# Add items to an existing playlist
client.add_to_playlist(
    playlist_id=playlist.id,
    items=["54321"]
)
```

### 3. Control Playback

```python
# Pause playback
client.pause_playback("Living Room TV")

# Skip to next item
client.next("Living Room TV")

# Set volume (0-100)
client.set_volume("Living Room TV", 50)
```

### 4. Library Management

```python
# Refresh a library
client.refresh_library(library_id=1)

# Scan for new files
client.scan_library(library_id=1)

# Get recently added items
recent = client.get_recently_added(library_id=1, limit=10)
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
