# MCP tools (portmanteau)

PlexMCP registers **portmanteau** tools: one tool per domain with an `operation` parameter (FastMCP 3.2, rich docstrings, structured errors).

## Highlights

| Tool | Role |
|------|------|
| `plex_server` | Status, info, health, maintenance |
| `plex_library` | Libraries: list, get, scan, refresh, … |
| `plex_media` | Browse, search, details, metadata |
| `plex_search` | Keyword / advanced search, suggestions |
| `plex_streaming` | Sessions, clients, playback control (capabilities vary by Plex API) |
| `plex_playlist` | Playlists CRUD and items |
| `plex_user` | Users and permissions |
| `plex_rag` | `sync_metadata`, `semantic_search` — see [RAG.md](RAG.md) |
| `arr_stack` | Optional Radarr/Sonarr/Lidarr **read-only** HTTP status (requires env URLs + API keys) |
| `agentic_plex_workflow` | Multi-step agentic flow with sampling (`sample_step`) |
| `plex_natural_assistant` | Single-turn natural language via sampling |

Additional portmanteau tools include `plex_metadata`, `plex_organization`, `plex_performance`, `plex_reporting`, `plex_collections`, `plex_quality`, `plex_integration`, `plex_help`, `plex_audio_mgr`, and related helpers — see source under `src/plex_mcp/tools/portmanteau/`.

## FastMCP 3.2 Features

- **Enhanced Error Handling**: All tools return structured error responses with proper error codes
- **Universal Connect**: Simultaneous stdio + HTTP access for multiple clients
- **Improved Validation**: Strict input validation with helpful error messages
- **Better Performance**: Optimized tool execution with connection pooling

## Tool Operations

Most tools support these common operations:

| Operation | Description |
|-----------|-------------|
| `list` | List available items |
| `get` | Get detailed information |
| `search` | Search within the domain |
| `create` | Create new items |
| `update` | Update existing items |
| `delete` | Remove items |
| `refresh` | Refresh data from Plex |

### Example Usage

```python
# List libraries
result = await mcp.call_tool("plex_library", {"operation": "list"})

# Get specific media details
result = await mcp.call_tool("plex_media", {
    "operation": "get",
    "library_id": 1,
    "item_id": 12345
})

# Search for content
result = await mcp.call_tool("plex_search", {
    "operation": "search",
    "query": "action movies",
    "library_id": 1
})
```

## Responses

Tools return JSON-friendly dicts with `success`, `operation`, and either `data` or `error` / `error_code` / `suggestions` for failures.

### Success Response
```json
{
    "success": true,
    "operation": "list",
    "data": {
        "libraries": [...]
    }
}
```

### Error Response
```json
{
    "success": false,
    "operation": "get",
    "error": "Library not found",
    "error_code": "NOT_FOUND",
    "suggestions": ["Use 'list' operation to see available libraries"]
}
```

## Monitoring and Health

Use the built-in health check to monitor server status:

```python
# Get server health
health = await mcp.read_resource("resource://plex/health")
```

## Playback note

Some playback paths depend on Plex client APIs and may return `NOT_IMPLEMENTED` or limited support for certain clients. Check tool responses and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Error Handling

All tools include comprehensive error handling:
- **Connection errors**: Automatic retry with exponential backoff
- **Validation errors**: Clear, actionable error messages
- **Permission errors**: Helpful guidance on required permissions
- **Rate limiting**: Graceful handling of Plex API limits
