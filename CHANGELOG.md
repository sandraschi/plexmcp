# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.0] - 2026-02-26

### Added
- **Neural Media RAG Portmanteau** (`tools/portmanteau/plex_rag.py`): New unified search and synthesis tool for accessing context vectorized by LanceDB.
- **Agentic Synthesis API**: Expanded the webapp FastAPI backend with `POST /api/v1/search` and `POST /api/v1/chat` to expose backend capabilities directly to the Unified Search Hub in `mcp-central-docs` without necessitating MCP protocol bridging.

## [2.2.0] - 2026-02-04

### Added
- **MCPB Packaging**: Full implementation of standard MCPB bundles with optimized build patterns
- **Build Infrastructure**: Added `mcpb.json` and staging patterns for clean packaging

### Fixed
- **Startup Logic**: Standardized server execution via system Python (`python -m plex_mcp`)
- **Dependency Management**: Resolved missing `aiohttp`, `fastmcp`, and `plexapi` in system environment
- **Path Resolution**: Fixed `PYTHONPATH` issues in `mcp_config.json` for reliable module loading

## [Unreleased] - ALPHA

### Added
- **Movies webapp**: Plex poster images on movie cards and list (via Next.js image proxy `/api/image/...` to backend). Movie detail modal on card/list click: wider layout (max-w-4xl), full poster, metadata (year, duration, content rating, rating, studio, genres, directors, tagline, summary), **Play in Plex** button (opens Plex Web in new tab when Plex URL is set in Settings), Close and Escape to dismiss.
- **Settings RAG section**: **RAG / Indexing** block with "Reindex metadata" button calling `POST /api/rag/sync`; shows indexed count or error so reindexing is visible without going to Semantic search.
- **In-repo RAG fallback**: When mcp-central-docs vector store is unavailable, optional LanceDB + sentence-transformers fallback (install with `pip install plex-mcp-advanced[rag]`); see `src/plex_mcp/services/rag_ingestor.py`.
- **FastMCP 3.1 alignment**: Transport docstrings and help updated to 3.1; fleet launch and v1 search/chat routes moved from MCP app to webapp backend (`POST /api/fleet/launch`, `POST /api/v1/search`, `POST /api/v1/chat`). Prompt `plex_media_guide` for agentic workflows.
- **Semantic search page**: Webapp page `/search/semantic` with natural-language search over RAG index; **Sync / Index metadata** button to start RAG indexing from the UI (`POST /api/rag/sync`). Backend `GET /api/rag/semantic` and `plex_rag` in MCP client tool map.
- **Chat preprompt**: LLM chat receives a live system preprompt (MCP server tools, webapp pages, Plex server name/version, media libraries, integrations). Built in `webapp/backend/app/chat_context.py`; injected when `use_context: true` (default) in `POST /api/llm/chat`.
- **RAG over movie and music descriptions** - Metadata RAG (LanceDB) now indexes movie, show, and **music (artist)** libraries from Plex API. Searchable content includes title, plot/summary, year, genres, directors (movies/shows) and artist title/summary (music). Use `plex_rag(operation="sync_metadata")` then `plex_rag(operation="semantic_search", query="...")`. Data sourced from Plex server via API (no local DB).
- **Webapp (reservoir 10740/10741)**: Full browser UI with FastAPI backend and Next.js 15 frontend
  - **Glassmorphism UI**: Backdrop-blur panels, retractable sidebar, topbar
  - **Logger modal**: Tail of webapp log with level/filter (topbar)
  - **Help modal**: Tiered help content (basic/intermediate/advanced/expert)
  - **Local LLM stack**: Ollama/LM Studio/OpenAI-compatible chat (LLM_BASE_URL, LLM_API_KEY)
  - **Advanced chat**: Personalities, prompt refining via LLM, chat export (MD/JSON)
  - **Light RAG**: GET /api/rag/context for Plex search context injection
  - **AI workflows**: POST /api/workflows/run (e.g. search_and_summarize)
  - **Semantic search**: Keyword search + RAG context for chat
  - **Movies page**: Pagination (page/limit in URL, offset to backend), card/list view toggle (persisted in localStorage)
  - **Settings page**: Plex API key and URL, LLM provider (ollama/lmstudio/openai), base URL, API key, default model (from /api/llm/models); persisted via GET/PATCH /api/system/settings and backend data/settings.json (file overrides .env at runtime)
  - **Start**: webapp/start.ps1 and start.bat; see webapp/SETUP.md
- **Port reservoir**: Backend 10740, frontend 10741 (mcp-central-docs WEBAPP_PORTS.md)
- **Next.js route /tools/get_system_status**: OPTIONS returns 204 (stops 404 from MCP clients probing); GET proxies to backend /api/server/status.

### Changed
- **RAG dependency** documented in README and Semantic search page: semantic search requires mcp-central-docs **source** on path (not the mcp-central-docs MCP server running). Sync available from UI.
- **Webapp backend**: start.ps1 now runs the **FastAPI webapp backend** (`webapp/backend/app/main:app`) on 10740 instead of the MCP-only app. Backend exposes all REST routes (`/api/server/*`, `/api/libraries/*`, `/api/search`, `/api/movies`, `/api/system/*`, `/api/logs`, `/api/help`, `/api/llm/*`, `/api/webapp-launch`, etc.) and mounts FastMCP at `/mcp`. Fixes 404/502 when frontend proxies to backend.
- **Start script**: Backend is launched with `.venv\Scripts\python.exe -m uvicorn app.main:app` (PYTHONPATH includes repo `src` and `webapp/backend`) so the venv is used directly and `uv sync` is not run at start (avoids "file in use" when venv is locked).
- **Fleet ports**: Frontend proxy default `BACKEND_URL` is `http://127.0.0.1:10740`; start.ps1 uses backend 10740, frontend 10741.
- **Next.js 15**: Removed invalid `--host` from npm dev script (Next 15 uses `--hostname`; default binds all interfaces). Removed invalid `turbopack` key from next.config.js (clears config warning).
- **CORS**: Added Starlette CORSMiddleware to FastMCP `http_app()` (allowed origins: localhost:10741, 127.0.0.1:10741, and 10740 variants) so browser/WebSocket connections from the frontend no longer get 403.
- **Dependencies**: Added `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `httpx`, `python-multipart` to root pyproject.toml so the webapp backend runs with the project venv.
- Updated project status to ALPHA in README; alpha status badge and warning notice.
- Next.js frontend pinned to 15.2.0 (webpack dev); turbopack config removed for Next 15 compatibility.
- Backend config loads .env from webapp/backend path (not cwd) so token is found when started from any directory.
- Backend data/ and settings.json in .gitignore (secrets not committed).

### Status
- **Project Status**: ALPHA - Active development, some features incomplete
- **Known Issues**: Playback control (`plex play`, `plex pause`) is non-functional for ALL clients
  - GDM clients (PlexAmp): Discoverable but playback commands fail
  - Non-GDM clients (Plex Web, Plex for Windows): Not controllable via tested API endpoints
- **See**: [STATUS_2026-01-08.md](STATUS_2026-01-08.md) for detailed status

### Fixed
- Client discovery now finds all client types (PlexAmp, Plex Web, Plex for Windows)
- Multi-source client discovery implementation

### Known Limitations
- Playback control (`plex play`, `plex pause`) fails for ALL clients
- GDM clients (PlexAmp): Discoverable via GDM but `plexapi_client.playMedia()` calls fail
- Non-GDM clients (Plex Web, Plex for Windows): Not controllable via tested API endpoints
- Server API endpoints tested don't work for any client type
- Root cause may be API endpoint parameters, authentication, or client state requirements

## [2.1.0] - 2025-11-22

### Added
- **Portmanteau Tool Architecture**: Complete refactoring from 52+ individual tools to 15 comprehensive portmanteau tools
- **15 Portmanteau Tools**: Consolidated related operations into unified interfaces
  - `plex_library` - Library management (12 operations)
  - `plex_media` - Media operations (5 operations)
  - `plex_user` - User management (6 operations)
  - `plex_playlist` - Playlist management (8 operations)
  - `plex_streaming` - Playback control (10 operations)
  - `plex_performance` - Performance & quality (13 operations)
  - `plex_metadata` - Metadata management (7 operations)
  - `plex_organization` - Library organization (5 operations)
  - `plex_server` - Server management (6 operations)
  - `plex_integration` - Third-party integrations (6 operations)
  - `plex_search` - Advanced search (5 operations)
  - `plex_reporting` - Analytics & reports (6 operations)
  - `plex_collections` - Collections management (7 operations)
  - `plex_quality` - Quality profiles (6 operations)
  - `plex_help` - Help & discovery (4 operations)
- **FastMCP 2.13+ Compliance**: All tools use Literal types for operation parameters
- **Comprehensive Docstrings**: Standardized docstrings with PORTMANTEAU PATTERN RATIONALE sections
- **Structured Error Handling**: AI-friendly error responses with suggestions

### Changed
- **Tool Count**: Reduced from 52+ individual tools to 15 portmanteau tools (71% reduction)
- **Tool Registration**: Only portmanteau tools are now loaded by default
- **Server Architecture**: Simplified tool imports in `server.py`
- **Documentation**: Updated README and documentation to reflect portmanteau architecture

### Deprecated
- **Old Individual Tools**: All individual tool files (`tools/library.py`, `tools/media.py`, etc.) are deprecated
- **API Tools**: `api/vienna.py` tools are deprecated in favor of `plex_integration`

### Fixed
- **Tool Registration**: Fixed import issues preventing tools from being registered
- **FastMCP Compliance**: Removed `**kwargs` from tool signatures (not supported by FastMCP)
- **Error Messages**: Improved error handling with structured responses

### Technical Details
- **FastMCP Version**: 2.13+ with Literal type support
- **Total Operations**: 106+ operations consolidated into 15 tools
- **Backward Compatibility**: Old tools remain in codebase but are not loaded by default

## [2.0.0] - 2025-10-10

### Added
- **MCPB Packaging**: Complete MCPB (MCP Bundle) implementation for one-click Claude Desktop installation
- **23 Powerful Tools**: Comprehensive Plex Media Server integration with 23 tools across 6 categories
- **User Configuration**: Interactive setup prompts for Plex URL and authentication token
- **Professional Documentation**: Complete documentation suite with 21 files and 400+ pages
- **GLAMA Integration**: Gold Status certification with 85/100 quality score
- **CI/CD Pipeline**: Automated testing, building, and publishing workflows
- **Plugin Ecosystem**: Support for 1,400+ Notepad++ plugins (adapted for PlexMCP)
- **Vienna AI Features**: European content discovery and anime season information
- **Advanced Error Handling**: Enterprise-grade error management and logging

### Changed
- **Framework Upgrade**: Migrated from DXT to MCPB packaging format
- **Tool Count**: Increased from 20 to 23 tools (+15% improvement)
- **Documentation**: Enhanced from basic to professional level (21 files vs 17)
- **Quality Score**: Achieved Gold Status (85/100) on GLAMA.ai platform
- **Testing**: Expanded test suite with comprehensive coverage

### Fixed
- **Import Issues**: Resolved plexapi dependency and module loading problems
- **Build Process**: Fixed MCPB CLI integration and packaging workflow
- **Configuration**: Improved environment variable handling and settings validation
- **Logging**: Implemented structured logging throughout the application

### Technical Details
- **Python Version**: >=3.10.0 (tested on 3.10-3.13)
- **FastMCP**: >=2.10.0 with MCP 2.12.0 compliance
- **PlexAPI**: >=4.15.0 for Plex Media Server integration
- **Platforms**: Windows, Linux, macOS support
- **Package Size**: 5.0 MB (optimized for distribution)

## [1.0.0] - 2025-09-15

### Added
- Initial Plex Media Server MCP integration
- Basic media library browsing and search functionality
- User management and permissions handling
- Playlist creation and management
- Playback control for connected clients
- Server health monitoring and maintenance tools

### Technical Details
- **Framework**: FastMCP 2.0
- **Protocol**: MCP 2.0 stdio
- **Tools**: 20 core tools
- **Documentation**: Basic setup and usage guides

---

## Types of changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Version History
- **2.0.0**: Production-ready with MCPB packaging and GLAMA Gold Status
- **1.0.0**: Initial release with basic Plex Media Server integration
