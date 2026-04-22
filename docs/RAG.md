# RAG and semantic search

Semantic search uses the **`plex_rag`** portmanteau tool:

- **`sync_metadata`** — index movie, show, and music (artist) metadata from Plex into LanceDB.
- **`semantic_search`** — query natural language over that index.

## Dependency

The **mcp-central-docs** repository provides `docs_mcp.backend.rag_core` (shared vector store). Add the `src` folder of that clone to `PYTHONPATH`, or install the package if published. The **mcp-central-docs MCP server does not need to be running**; only the Python library is used.

If the import fails, `plex_rag` reports unavailability and the webapp **Semantic search** page shows that RAG is not available.

### Verify the vector dependency (before filing issues)

With **mcp-central-docs** cloned next to plex-mcp, point `PYTHONPATH` at its `src` (paths are examples — adjust to your layout).

**Windows (PowerShell), from the plex-mcp repo root** (sibling folder `mcp-central-docs`):

```powershell
$env:PYTHONPATH = "D:\Dev\repos\mcp-central-docs\src"
uv run python -c "import docs_mcp.backend.rag_core; print('rag_core OK')"
```

**macOS / Linux (bash), sibling checkout:**

```bash
export PYTHONPATH="/path/to/mcp-central-docs/src"
uv run python -c "import docs_mcp.backend.rag_core; print('rag_core OK')"
```

If you see `ModuleNotFoundError: docs_mcp`, the path is wrong or the clone is missing. RAG and semantic search **require** this import to succeed in the process that runs `plex_mcp` (including the webapp backend).

## First-time index

Run once before querying:

- MCP: `plex_rag(operation="sync_metadata", enrich=False)` (Standard sync), or  
- MCP (Deep): `plex_rag(operation="sync_metadata", enrich=True)` (Enriched sync), or
- Subtitles: `plex_rag(operation="sync_subtitles")` (Dialogue indexing), or
- Webapp: **Semantic search** → “Sync / Index metadata”, or **Settings** → **RAG / Indexing** → Reindex.

Large libraries may take minutes; the first run may download the embedding model.

## Dialogue RAG (Subtitle Neural Search)

As of **v2.5.0**, PlexMCP supports deep semantic search across media dialogue:
- **Automatic Discovery**: Identifies text-based subtitle tracks (SRT, VTT) for Movies and TV Episodes.
- **Timestamped Snippets**: Search results include the exact time in the media where the dialogue occurs.
- **Dialogue Normalization**: The parser strips HTML tags and formatting to ensure high-fidelity embeddings.
- **Conversational Context**: Subtitles are grouped into overlapping windows to preserve dialogue flow.

### Usage
- MCP: `plex_rag(operation="sync_subtitles")`
- MCP Search: `plex_rag(operation="search_subtitles", query="I'll be back")`
- Webapp: **Search** → Toggle mode to **Dialogue**.

> [!NOTE]
> Image-based subtitles (PGS, VOBSUB) are currently not supported as they require OCR.

## Deep Indexing (Industrial)

As of version 2.4.0, PlexMCP implements **Deep Indexing**:
- **TV Shows**: Automatically traverses all seasons and indexes every episode individually.
- **Music**: Traverses all artists and indexes every album individually.
- **Hierarchical Context**: Content strings are enriched with grandparent/parent metadata.

### High-Value Augmentation (v2.4.1)

You can now augment your RAG index with deep contextual data from Wikipedia during the sync process:
- **`enrich=True`**: Appends historical era, thematic summaries, and narrative context to each document.
- **Search Impact**: Significantly improves results for "Informed Discovery" (e.g., searching by time period or cultural significance).

For detailed usage, see [**docs/ENRICHMENT.md**](ENRICHMENT.md).

## Telemetry and Control

The webapp provides an **Industrial RAG Management** dashboard with real-time telemetry:
- **Streaming Logs**: Track exactly which library and item is being indexed in real-time.
- **Vector Stats**: Monitor document counts for both **Metadata** and **Dialogue** stores.
- **Sync Control**: Trigger full or incremental syncs for metadata or subtitles directly from the UI.
