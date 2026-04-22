# High-Value Media Enrichment

PlexMCP provides advanced "Informed Discovery" capabilities by fetching contextual metadata from external high-value sources that are not natively available in Plex Media Server.

## Overview

The enrichment system specifically targets narrative context, historical era data, and cultural trivia. By augmenting standard Plex metadata with these insights, the AI assistant can provide much deeper analysis and thematic recommendations.

### Key Sources
- **Wikipedia**: Primary source for narrative summaries, historical context, and cultural impact.
- **TMDB / TVDB / TV Tropes**: Linked metadata for external exploration.

---

## Standalone Enrichment

You can proactively enrich a specific media item using the **`plex_media_enrichment`** portmanteau tool.

### Operations
- **`enrich_item`**: Fetches a deep summary and contextual description from Wikipedia.
- **`get_external_metadata`**: Generates high-fidelity links to external databases (TMDB, TVDB, TV Tropes).

### Example Usage
```python
# Fetch deep Wikipedia context for a movie
plex_media_enrichment(
    operation="enrich_item",
    title="Blade Runner 2049",
    year=2017,
    media_type="movie"
)
```

---

## RAG Augmentation (Deep Indexing)

The most powerful application of enrichment is within the **Neural Media RAG** synchronization pipeline.

When syncing your library metadata into the LanceDB vector store, you can enable the `enrich` flag to augment every indexed item with Wikipedia context.

### Enabling Enrichment in RAG
```python
# Sync library metadata with automatic Wikipedia enrichment
plex_rag(operation="sync_metadata", enrich=True)
```

### Why use Enriched RAG?
- **Thematic Search**: Find movies based on era or mood (e.g., *"Find me films set in the Victorian era"* or *"Space operas with social commentary"*).
- **Nuanced Recommendations**: The LLM can "read" the Wikipedia summary stored in the index to explain *why* a movie matches your query.
- **Improved Semantic Accuracy**: Appending narrative summaries to the standard plot improves the embedding's "signal" for complex queries.

---

## Performance and Rate Limiting

The enrichment service implements built-in industrial safeguards:
- **Semaphore-based Concurrency**: Limits concurrent API requests to Wikipedia to avoid rate-limiting or IP bans (default: 5 concurrent requests).
- **Lazy Loading**: Enrichment only triggers if the `enrich` flag is explicitly set or if a manual tool is called.
- **Structured Caching**: Enriched data is stored directly in the LanceDB index to ensure high-speed recall during semantic search without repeatedly hitting external APIs.

---

## Technical Details

- **Backend Service**: `src/plex_mcp/services/enrichment_service.py`
- **Tool Logic**: `src/plex_mcp/tools/portmanteau/enrichment.py`
- **API**: Wikipedia REST API (`/api/rest_v1/page/summary/`)

> [!TIP]
> Use `plex_rag(operation="status")` to check if your current index is enriched. An enriched index will typically show a "Deep Context" message in the status output.
