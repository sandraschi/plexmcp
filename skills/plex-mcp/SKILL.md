---
name: plex-mcp
description: Manage a Plex Media Server via 22 portmanteau MCP tools (libraries, media, search, streaming, users, playlists, metadata, performance, reports, RAG, taste, enrichment, arr, lifecycle). Use when the task touches Plex libraries, playback, users, or media metadata.
---

# PlexMCP skill

Talk to a Plex Media Server through portmanteau tools — one tool per domain,
each with an `operation` parameter. Never invent identifiers, URLs, or tokens;
discover them first.

## Session startup

1. `plex_server(operation="status")` — reachable? version? load?
2. `plex_library(operation="list")` — sections, types, sizes.
3. `plex_rag(operation="status")` — only when the task needs semantic search.

## Tool surface (24 tools)

| Tool | Key operations |
|---|---|
| `plex_library` | list, get, list_items, create, scan, refresh, optimize, empty_trash (!), add/remove_location, delete (!) |
| `plex_media` | browse, search, get_details, get_recent, get_stream_url, update_metadata |
| `plex_search` | search, advanced_search, suggest, recent_searches, save_search |
| `plex_streaming` | list_sessions, list_clients, play, pause, stop, seek, control |
| `plex_server` | status, info, health, maintenance, restart (!), update (!) |
| `plex_user` | list, get, create, update, delete (!), update_permissions |
| `plex_playlist` | list, get, create, update, delete (!), add/remove_items, get_analytics |
| `plex_collections` | list, get, create, update, delete (!), add/remove_items |
| `plex_metadata` | analyze, match, fix_match, refresh, refresh_all, update, organize |
| `plex_organization` | analyze, organize, fix_issues, clean_bundles, optimize_database |
| `plex_performance` | transcode getters before setters; set_quality, throttling, profiles |
| `plex_quality` | list/get/create/update/delete profiles, set_default |
| `plex_reporting` | library_stats, content_report, user_activity, usage/performance reports, export_report (json/csv/html) |
| `plex_rag` | status, sync_metadata, sync_subtitles, semantic_search, search_subtitles |
| `plex_taste` | status, rebuild_from_history, sync, profile, score_item, score_library |
| `plex_media_enrichment` | enrich, bulk_enrich, get_enrichment, get_related, search_by_theme/person, stale_report |
| `plex_integration` | list_integrations, vienna_recommendations, european_content, anime_season_info, configure, sync |
| `plex_audio_mgr` | list/select streams, volume, mute, handover |
| `plex_ffmpeg_mgr` | probe first, then sync/extract operations, revert |
| `arr_stack` | status (read-only Radarr/Sonarr/Lidarr snapshot) |
| `plex_help` | help, list_tools, tool_info, examples, api_docs |
| `plex_shutdown` | status, shutdown (!) |
| `agentic_plex_workflow` | orchestrate (needs sampling or `PLEX_SAMPLING_BASE_URL`) |
| `plex_natural_assistant` | answer (no tools) |

`(!)` needs explicit user confirmation (destructive or interruptive).

## Workflow 1 — triage an unknown server

`plex_server status` → `plex_library list` → summarize versions, sections,
anything offline. Unreachable: check URL/token via the webapp Settings PIN
flow, do not retry blindly.

## Workflow 2 — fix a bad metadata match

Search → `plex_media get_details` (confirm the wrong match) →
`plex_metadata match` (candidate hits) → `fix_match` → `refresh` →
`get_details` again to verify art and cast.

## Workflow 3 — semantic discovery

`plex_rag status` → if empty, `sync_metadata` (warn: minutes to hours) →
`semantic_search` in the user's words → `search_subtitles` for quoted
dialogue. Keyword search never needs the index.

## Safety

Confirm before: empty_trash, delete (library/playlist/user), remove_location,
PMS restart/update, killing others' sessions, server shutdown. Reads and
searches never need confirmation. Tokens live in env/keystore — use the
webapp PIN flow, never paste secrets. Verify every write with its paired
read (update→get_details, add_items→get, setter→getter→live session).
