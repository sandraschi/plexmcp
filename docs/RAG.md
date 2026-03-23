# RAG and semantic search

Semantic search uses the **`plex_rag`** portmanteau tool:

- **`sync_metadata`** — index movie, show, and music (artist) metadata from Plex into LanceDB.
- **`semantic_search`** — query natural language over that index.

## Dependency

The **mcp-central-docs** repository provides `docs_mcp.backend.rag_core` (shared vector store). Add the `src` folder of that clone to `PYTHONPATH`, or install the package if published. The **mcp-central-docs MCP server does not need to be running**; only the Python library is used.

If the import fails, `plex_rag` reports unavailability and the webapp **Semantic search** page shows that RAG is not available.

## First-time index

Run once before querying:

- MCP: `plex_rag` with `operation="sync_metadata"`, or  
- Webapp: **Semantic search** → “Sync / Index metadata”, or **Settings** → **RAG / Indexing** → Reindex (with progress UI).

Large libraries may take minutes; the first run may download the embedding model.
