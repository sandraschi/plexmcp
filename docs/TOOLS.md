# MCP tools (portmanteau)



PlexMCP registers **portmanteau** tools: one tool per domain with an `operation` parameter (FastMCP 3.1, rich docstrings, structured errors).



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

| `plex_rag` | `sync_metadata`, `sync_subtitles`, `semantic_search`, `search_subtitles` — see [RAG.md](RAG.md) |

| `arr_stack` | Optional Radarr/Sonarr/Lidarr **read-only** HTTP status (requires env URLs + API keys) |

| `agentic_plex_workflow` | Multi-step agentic flow with sampling (`sample_step`) |

| `plex_natural_assistant` | Single-turn natural language via sampling |



Additional portmanteau tools include `plex_metadata`, `plex_organization`, `plex_performance`, `plex_reporting`, `plex_collections`, `plex_quality`, `plex_integration`, `plex_help`, `plex_audio_mgr`, and related helpers — see source under `src/plex_mcp/tools/portmanteau/`.



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

