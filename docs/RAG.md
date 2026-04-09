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

## Deep Indexing (Industrial)

As of version 2.4.0, PlexMCP implements **Deep Indexing**:
- **TV Shows**: Automatically traverses all seasons and indexes every episode individually.
- **Music**: Traverses all artists and indexes every album individually.
- **Hierarchical Context**: Content strings are enriched with grandparent/parent metadata:
  - **Episodes**: `Show: [Show Title]\nSeason [N], Episode [M]: [Title] \n [Plot]`
  - **Albums**: `Artist: [Artist Title]\nAlbum: [Title] \n [Summary]`

This contextual enrichment ensures that searches for plot details or album titles correctly associate with their parent metadata, enabling high-fidelity discovery (e.g., finding the specific episode where a specific event occurs).

## Telemetry and Control

The webapp provides an **Industrial RAG Management** dashboard with real-time telemetry:
- **Streaming Logs**: Track exactly which library and item is being indexed in real-time.
- **Vector Stats**: Monitor total document count in the vector store.
- **Sync Control**: Trigger full or incremental syncs directly from the UI.
