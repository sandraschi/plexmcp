# MCP tools (portmanteau)

PlexMCP registers **portmanteau** tools: one tool per domain with an `operation` parameter.
All 22 tools are FastMCP 3.2 aligned (`version="1.0.0"`, `annotations=READ_ONLY|MUTATING|DESTRUCTIVE`,
`Annotated[Field]` parameters, `ToolResult` returns, SOTA docstrings).



## Tool inventory

| Tool | Annotations | Role |
|------|-------------|------|
| `plex_server` | `MUTATING` | Status, info, health, maintenance |
| `plex_library` | `DESTRUCTIVE` | Libraries: list, get, create, update, delete, scan, refresh, optimize |
| `plex_media` | `MUTATING` | Browse, search, details, metadata (browse/search: read, update_metadata: write) |
| `plex_search` | `MUTATING` | Keyword / advanced search, suggestions |
| `plex_streaming` | `MUTATING` | Sessions, clients, playback control (capabilities vary by Plex API) |
| `plex_playlist` | `DESTRUCTIVE` | Playlists CRUD and items |
| `plex_user` | `MUTATING` | Users and permissions |
| `plex_rag` | `MUTATING` | `sync_metadata`, `sync_subtitles`, `semantic_search`, `search_subtitles` \u2014 see [RAG.md](RAG.md) |
| `plex_performance` | `MUTATING` | Server performance metrics, bandwidth, transcodes |
| `plex_metadata` | `MUTATING` | Metadata refresh, update, organization |
| `plex_organization` | `MUTATING` | Library organization, clean bundles, optimize database |
| `plex_collections` | `MUTATING` | Collection management |
| `plex_quality` | `DESTRUCTIVE` | Quality profiles, transcoding settings |
| `plex_reporting` | `READ_ONLY` | Server statistics, usage reports, activity logs |
| `plex_integration` | `MUTATING` | Third-party integration setup and sync |
| `plex_help` | `READ_ONLY` | Tool discovery, capability overview |
| `plex_audio_mgr` | `MUTATING` | Audio stream management |
| `plex_ffmpeg_mgr` | `DESTRUCTIVE` | FFmpeg process management |
| `plex_media_enrichment` | `READ_ONLY` | Wikipedia-style enrichment |
| `arr_stack` | `READ_ONLY` | Optional Radarr/Sonarr/Lidarr HTTP status (requires env URLs + API keys) |
| `agentic_plex_workflow` | `MUTATING` | Multi-step agentic flow with sampling |
| `plex_natural_assistant` | `MUTATING` | Single-turn natural language via sampling |


## Prefab interactive cards

9 tools include Prefab UI cards rendered as `structured_content` on ToolResult.
These provide rich visual rendering in MCP clients that support Prefab:

| Card builder | Tool return context | Components |
|-------------|-------------------|------------|
| `build_library_grid` | `plex_library(operation="list")` | Grid of library cards with item counts |
| `build_library_detail` | `plex_library(operation="get")` | Library detail with metrics, locations |
| `build_media_browser` | `plex_media(browse/search/recent)`, `plex_search` | Grid of media cards with ratings |
| `build_media_detail` | `plex_media(operation="get_details")` | Full detail: summary, genres, cast, directors |
| `build_server_status` | `plex_server(operation="status")` | Server metrics: version, uptime, sessions |
| `build_server_info` | `plex_server(operation="info")` | Server info: platform, version, machine ID |
| `build_performance_dashboard` | `plex_performance` | Dashboard: streams, transcodes, bandwidth |
| `build_streaming_session` | `plex_streaming(operation="list_sessions")` | DataTable of active sessions |
| `build_streaming_client` | `plex_streaming(operation="list_clients")` | Connected client cards |

Source: `src/plex_mcp/prefabs.py` using `prefab_ui` v0.18.0 components (Card, Grid, Metric, DataTable, Badge).


## Suggested agent flows (pipelines)

Use these as **recipes** for tool-calling clients (not a strict API contract).

1. **“What can I watch?”** — `plex_library` → `list` → pick `library_id` → `plex_media` → `browse` with `media_type: movie` or `show` → `plex_media` → `get_details` on a `ratingKey`.
2. **“Find that title”** — `plex_search` → `search` with `query` (+ optional `library_id`) → read `ratingKey` from results → `plex_media` → `get_details` for summary and art paths.
3. **“Is the server healthy?”** — `plex_server` → `status` and/or `info` — then optionally `arr_stack` if *arr env is configured.
4. **RAG (after [RAG.md](RAG.md) is satisfied)** — `plex_rag` → `sync_metadata` once, then `semantic_search` (or `search_subtitles` for dialogue).

## Responses

Tools return JSON-friendly dicts with `success`, `operation`, and either `data` or `error` / `error_code` / `suggestions` for failures.



## Playback note



Some playback paths depend on Plex client APIs and may return `NOT_IMPLEMENTED` or limited support for certain clients. Check tool responses and [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

