## Session Context (Plex MCP)

You have access to a Plex Media Server management server with 20+ portmanteau tools
for library management, media browsing, streaming sessions, playlists, collections,
users, search, reporting, RAG semantic search, quality profiles, and server admin.

**Before starting work:**
1. Check server status: `plex_server(operation="status")`
2. Browse available libraries: `plex_library(operation="list")`
3. Semantic search for media context: `plex_rag(operation="semantic_search", query="<describe task>")`

**At end of work:**
- Use `plex_help(operation="list_tools")` to discover new capabilities
- Save useful searches with `plex_search(operation="save_search")`
