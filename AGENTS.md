# PlexMCP — Agent Context

## Project Overview

PlexMCP is an industrialized FastMCP 3.2 server for Plex Media Server.
It provides 22 MCP tools (portmanteau) for library/media/search/playlist management,
plus an optional FastAPI + Next.js webapp for browsing.

- Python 3.12+, FastMCP 3.2.0, `uv` package manager
- PlexAPI 4.17+, httpx 0.28.1+
- Webapp: Next.js 15.2, Tailwind CSS, FastAPI backend
- Ports: backend 10740, frontend 10741

## Key Commands

```powershell
# Lint
ruff check src/plex_mcp/ webapp/backend/     # Python
cd webapp/frontend && biome check .            # JS/TS

# Test
uv run pytest tests/test_portmanteau_*.py --tb=short -q

# Start webapp
cd webapp && powershell -ExecutionPolicy Bypass -File .\start.ps1

# Start MCP server only (stdio)
uv run plex-mcp-advanced

# Justfile
just lint       # ruff + biome
just test       # pytest
just fix        # ruff --fix + biome
just webapp     # start web interface
```

## Architecture

```
src/plex_mcp/
  app.py              # FastMCP instance creation (heavy, lazy-loaded by webapp)
  prefabs.py          # Prefab card builders (9 cards using prefab_ui)
  tools/portmanteau/  # 20 @mcp.tool() portmanteau tools
  tools/agentic.py    # 2 agentic tools (dynamic registration)
  services/           # PlexService, PlexMediaService, RAG, enrichment
  models/             # Pydantic v2 models (MediaItem, LibrarySection, etc.)

webapp/
  backend/app/
    main.py           # FastAPI app, lazy FastMCP mount
    api/
      images.py       # Image proxy (follow_redirects=True critical!)
      llm.py          # Ollama/OpenAI-compatible chat + model listing
      movies.py       # Movie listing endpoint
      library.py      # Library listing endpoint
      mcp/client.py   # Direct import tool caller (not HTTP subprocess)
  frontend/
    app/
      layout.tsx      # Root layout (suppressHydrationWarning on <html>)
      page.tsx        # Server component (force-dynamic)
      movies/         # Movies page (useSearchParams needs Suspense)
      settings/       # Settings page (LLM model elicitation)
    utils/
      plex-media-ui.ts  # plexImageUrl() -> /image/{path}
      api.ts          # All API fetch wrappers
    next.config.js    # Rewrites for /api/* and /image/* -> backend
```

## FastMCP 3.2 Patterns

All 22 tools use:

```python
from typing import Annotated
from pydantic import Field
from fastmcp.tools import ToolResult

@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def plex_tool(
    operation: Annotated[Literal["list", "get"], Field(description="...")],
    param: Annotated[str | None, Field(description="...")] = None,
) -> ToolResult:
    \"\"\"Summary.

    ## Return Format
    {"success": bool, "data": ..., "operation": "..."}

    ## Examples
    await tool(operation="list")
    \"\"\"
```

**Annotations** (dict form, not constants — FastMCP 3.2.0 doesn't export READ_ONLY etc.):
- `{"readOnlyHint": True}` — read-only tools
- `{"readOnlyHint": False, "destructiveHint": False}` — mutating (additive)
- `{"readOnlyHint": False, "destructiveHint": True}` — destructive

**Returns**: Always `ToolResult(content={...})`, optionally with `structured_content=PrefabApp(...)` for interactive cards and `meta={"prefabs": ["name"]}`.

## Prefab Cards

9 card builders in `src/plex_mcp/prefabs.py` using `prefab_ui` v0.18.0:

| Builder | Used by | Components |
|---------|---------|------------|
| `build_library_grid` | `plex_library("list")` | Grid, Card, Metric |
| `build_library_detail` | `plex_library("get")` | Grid, Metric, Badge |
| `build_media_browser` | `plex_media(browse/search/recent)`, `plex_search` | Grid, Card, Metric |
| `build_media_detail` | `plex_media("get_details")` | Card, Grid, Badge, Row |
| `build_server_status` | `plex_server("status")` | Grid, Metric, Badge |
| `build_server_info` | `plex_server("info")` | Grid, Metric |
| `build_performance_dashboard` | `plex_performance` | Grid, Metric |
| `build_streaming_session` | `plex_streaming("list_sessions")` | DataTable, Badge |
| `build_streaming_client` | `plex_streaming("list_clients")` | Grid, Card |

**IMPORTANT**: `Row`, `Column`, etc. in prefab_ui only support `with Row():` syntax — NOT `Row()(child1, child2)`. They don't have `__call__`.

## Image Proxy Pipeline

```
Browser <img src="/image/library/metadata/123/thumb/456">
  -> Next.js rewrite /image/:path* -> http://127.0.0.1:10740/image/{path}
  -> FastAPI /image/{path:path} -> httpx GET https://plex:32400/{path}?X-Plex-Token=...
  -> Plex returns image (possibly via 307 redirect to /photo/:/transcode)
```

**Critical**: httpx 0.27+ changed `follow_redirects` default to `False`.
Plex thumb endpoints redirect (307) to `/photo/:/transcode`. Always use
`httpx.AsyncClient(follow_redirects=True)` when proxying Plex images.

**URL pattern**: `plexImageUrl()` in `plex-media-ui.ts` produces `/image/{path}`.
The backend also has `/api/image/{path}` as fallback via `app.include_router(images.router, prefix="/api/image")`.

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Posters not showing | httpx follow_redirects=False | `AsyncClient(follow_redirects=True)` |
| | Next.js rewrite sends /api/image/... without stripping prefix | Add backend route at /api/image/{path} too |
| Hydration error | Dark Reader browser extension | `suppressHydrationWarning` on `<html>` |
| | `useSearchParams()` without Suspense | Wrap in `<Suspense>` boundary |
| 502 on API calls | Bad import in portmanteau tools (READ_ONLY etc don't exist) | Use dict annotations, not constants |
| | Backend not running or import failed | Check webapp.log for traceback |
| MediaItem has no .get() | Prefab builder receives model objects not dicts | `item.model_dump()` before passing to prefab |
| 'Row' object is not callable | `Row()(child)` syntax not supported | Use `with Row():` context manager |
| LLM models not loading | `loadModels` defined after `useEffect` that calls it | Move `loadModels` before `useEffect` |
| | Silent error catch | Add modelError state and display |
| Startup slow (~103s) | `from plex_mcp.app import http_app` imports fastmcp | Lazy-load in background via lifespan + create_task |
| next start broken | output: "standalone" in next.config.js | Use `npm run dev` instead for local dev |

## Pydantic v2

All models use `model_dump()` — NOT `.dict()` (Pydantic v1). The `_json_safe_media_item()`
helper in `client.py` handles both for backward compat.

## Test Patterns

Tests use `tool_payload()` from `tests/helpers.py` to unwrap `ToolResult` -> dict.
Mock PlexService via `tests/fixtures/mock_plex_service.py`.
73 portmanteau tests cover all 22 tools.

```python
def tool_payload(result):
    # Returns content dict (conversational), NOT structured_content (Prefab)
    # Priority: content dict > content list[TextContent] > structured_content
```

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
