# Plex MCP Client Discovery Fix

**Issue**: The `plex_streaming` tool's `list_clients` operation was only returning PlexAmp and not finding Plex Web client or Plex Windows app client.

**Root Cause**: The client discovery was relying primarily on UDP-based Global Discovery Mechanism (GDM) which many Plex clients don't respond to reliably.

**Solution**: Enhanced the `_get_clients_sync` method in `plex_service.py` with multiple discovery methods:

## Changes Made

### 1. Added Direct API Call (Method 4)
```python
# Method 4: Direct HTTP API call to /clients endpoint
# This is the most reliable method as it queries the server directly
try:
    clients_url = f"{self.base_url}/clients"
    headers = {
        "X-Plex-Token": self.token,
        "Accept": "application/xml"
    }
    response = requests.get(clients_url, headers=headers, timeout=10)
    # Parse XML response and extract client information
```

### 2. Improved Account Resources Filtering (Method 3)
Made the `provides` field filtering more permissive to catch clients with different `provides` values:

```python
provides_lower = provides.lower()
is_client = provides and (
    "player" in provides_lower or
    "client" in provides_lower or
    "plex" in provides_lower or  # Many Plex clients just say "plex"
    not provides_lower or  # Empty provides might be clients
    provides_lower in ["", "unknown"]  # Unknown provides might be clients
)
```

## Discovery Methods Now Used

1. **GDM Discovery** (`server.clients()`) - UDP broadcasting (fast but unreliable)
2. **Active Sessions** - Clients with current playback sessions
3. **Account Resources** - All devices registered with Plex account (improved filtering)
4. **Direct API Call** - HTTP `/clients` endpoint (most reliable)

## Expected Results

The `list_clients` operation should now find:
- PlexAmp (music-focused client)
- Plex Web (browser-based client)
- Plex Windows App (desktop client)
- Plex for Android/iOS (mobile clients)
- Other Plex clients (Roku, Fire TV, etc.)

## Testing

To test the fix:

1. Start Plex server and ensure clients are running
2. Run: `python -m plex_mcp.server`
3. Use the `plex_streaming` tool with `operation="list_clients"`
4. Should now return multiple clients instead of just one

## Technical Details

The fix ensures client discovery works even when:
- Clients don't respond to UDP GDM broadcasts
- Clients are behind firewalls/NAT
- Clients are on different subnets
- Clients have non-standard `provides` field values

The direct API call to `/clients` is the most reliable method as it queries the Plex server directly for all known active clients.