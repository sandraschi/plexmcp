# Configuration

## Environment Setup

Create a `.env` file in the project root:

```env
# Plex server connection (required)
PLEX_BASE_URL=http://localhost:32400
PLEX_TOKEN=your-x-plex-token

# FastMCP Settings
PLEXMCP_ALLOW_LOGGING=1
PLEX_SAMPLING_USE_CLIENT_LLM=1

# Optional: Server-side LLM sampling
# PLEX_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1
# PLEX_SAMPLING_MODEL=llama3.2
# PLEX_SAMPLING_API_KEY=your-api-key

# Optional: *arr integration
# RADARR_URL=http://localhost:7878
# RADARR_API_KEY=your-radarr-key
# SONARR_URL=http://localhost:8989
# SONARR_API_KEY=your-sonarr-key
# LIDARR_URL=http://localhost:8686
# LIDARR_API_KEY=your-lidarr-key
```

## Plex (required)

| Variable | Description |
|----------|-------------|
| `PLEX_TOKEN` | X-Plex-Token (required) |
| `PLEX_URL` / `PLEX_SERVER_URL` / `PLEX_BASE_URL` | Base URL of Plex (default `http://127.0.0.1:32400`) |

**Getting your Plex Token:**
1. Open Plex Web App
2. Go to **Settings → Account → Authorized devices**
3. Copy the **X-Plex-Token** value

## FastMCP Settings

| Variable | Description |
|----------|-------------|
| `PLEXMCP_ALLOW_LOGGING` | Enable detailed logging (set to `1`) |
| `PLEX_SAMPLING_USE_CLIENT_LLM` | Use client-side LLM sampling (recommended: `1`) |

## Sampling (optional)

Server-side LLM for `plex_natural_assistant` / agentic flows when the host does not sample:

| Variable | Description |
|----------|-------------|
| `PLEX_SAMPLING_BASE_URL` | OpenAI-compatible API base (e.g. Ollama `http://127.0.0.1:11434/v1`) |
| `PLEX_SAMPLING_MODEL` | Model name (default: `llama3.2`) |
| `PLEX_SAMPLING_API_KEY` | API key for cloud LLM services |
| `PLEX_SAMPLING_USE_CLIENT_LLM` | Set to `1` to prefer the MCP client's LLM when supported |

**Recommended Setup:** Use `PLEX_SAMPLING_USE_CLIENT_LLM=1` for best performance.

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

## Deployment Configuration

### Environment Variables for Production

```env
# Production settings
PLEXMCP_ALLOW_LOGGING=0  # Disable verbose logging in production
PLEX_SAMPLING_USE_CLIENT_LLM=1

# Monitoring (optional)
MONITORING_ENABLED=1
HEALTH_CHECK_INTERVAL=30
```

### Transport Configuration

| Variable | Description |
|----------|-------------|
| `MCP_TRANSPORT` | Transport mode: `stdio`, `http`, or `sse` (default: `stdio`) |
| `MCP_HOST` | Bind address for HTTP/SSE (default: `127.0.0.1`) |
| `MCP_PORT` | Port for HTTP/SSE (default: `10740`) |
| `MCP_PATH` | HTTP endpoint path (default: `/mcp`) |
