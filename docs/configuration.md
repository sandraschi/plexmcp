# Configuration

## Plex (required)

| Variable | Description |
|----------|-------------|
| `PLEX_TOKEN` | X-Plex-Token (required) |
| `PLEX_URL` / `PLEX_SERVER_URL` | Base URL of Plex (default `http://127.0.0.1:32400`) |

## Sampling (optional)

Server-side LLM for `plex_natural_assistant` / agentic flows when the host does not sample:

| Variable | Description |
|----------|-------------|
| `PLEX_SAMPLING_BASE_URL` | OpenAI-compatible API base (e.g. Ollama `http://127.0.0.1:11434/v1`) |
| `PLEX_SAMPLING_USE_CLIENT_LLM` | Set to `1` to prefer the MCP client’s LLM when supported |

## RAG / semantic search

The `plex_rag` tool (LanceDB + embeddings) needs shared vector code importable as `docs_mcp.backend.rag_core` (e.g. clone [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) and add its `src` to `PYTHONPATH`). See [RAG.md](RAG.md).

## *arr stack (optional)

Read-only HTTP status for Radarr / Sonarr / Lidarr when set:

| Variable | Description |
|----------|-------------|
| `RADARR_URL`, `RADARR_API_KEY` | Base URL + API key |
| `SONARR_URL`, `SONARR_API_KEY` | Same |
| `LIDARR_URL`, `LIDARR_API_KEY` | Same |

Usually set via the **webapp Settings** page (stored in `webapp/backend/data/settings.json` and applied to the process environment).

## Webapp overrides

The FastAPI backend loads `webapp/backend/data/settings.json` at startup and merges Plex, LLM, and *arr keys into `os.environ`. See [WEBAPP.md](WEBAPP.md).
