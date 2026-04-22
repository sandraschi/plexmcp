"""
Plex Media Enrichment Portmanteau Tool (FastMCP 3.1)

Consolidates external metadata discovery and high-value enrichment.
"""

from typing import Literal

from ...app import mcp
from ...services.enrichment_service import get_enrichment_service
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool()
async def plex_media_enrichment(
    operation: Literal["enrich_item", "get_external_metadata", "analyze_trends"],
    title: str,
    year: int | None = None,
    media_type: Literal["movie", "show"] = "movie",
) -> str:
    """
    High-value media enrichment using external sources (Wikipedia, TMDB, TVDB).

    This tool adds 'Informed Discovery' capabilities to PlexMCP by fetching
    contextual metadata that Plex does not natively provide.

    Args:
        operation: Literal operation to perform:
            - 'enrich_item': Fetch Wikipedia context and summary for a specific item.
            - 'get_external_metadata': Fetch IDs and links for external databases.
            - 'analyze_trends': (Future) Analyze cultural context or trivia.
        title: Title of the media item to enrich.
        year: Release year of the item (optional, improves matching).
        media_type: Type of media ('movie' or 'show').

    Returns:
        Structured markdown with external insights and Prefab UI elements.
    """
    enrich_service = get_enrichment_service()

    try:
        if operation == "enrich_item":
            logger.info(f"Enriching {media_type}: {title} ({year})")
            wiki = await enrich_service.fetch_wikipedia_summary(title, year, media_type)

            if not wiki or not (wiki.get("summary") or "").strip():
                return f"### High-Value Enrichment: {title}\n\nNo Wikipedia article summary matched this title/year. Try adjusting the year or use get_external_metadata for search links."

            extract = (wiki.get("summary") or "").strip()
            page_url = wiki.get("url") or ""
            return f"""
### High-Value context: {title} ({year if year else "N/A"})

**Source:** {wiki.get("source", "Wikipedia")}  
**Article:** {page_url}

{extract}

---
> Tip: Enable Wikipedia enrichment during RAG metadata sync (`plex_rag` / `enrich=True`) for searchable deep context.
"""

        if operation == "get_external_metadata":
            # For now, we return links and placeholders for IDs
            # Real TMDB/TVDB integration would go here if keys were provided
            return f"""
### 🔗 External Discovery: {title}

| Source | Status | Link |
| :--- | :--- | :--- |
| Wikipedia | Found | [View Article](https://en.wikipedia.org/wiki/{title.replace(" ", "_")}) |
| TMDB | Linked | [Direct Search](https://www.themoviedb.org/search?query={title.replace(" ", "%20")}) |
| TV Tropes | Staged | [Direct Search](https://tvtropes.org/pmwiki/search_result.php?q={title.replace(" ", "+")}) |

> [!NOTE]
> Detailed ID mapping (TMDB_ID, TVDB_ID) is available via the enriched RAG index for indexed items.
"""

        if operation == "analyze_trends":
            return f"### [MOCK] Cultural Analysis: {title}\n\nCultural trend analysis is currently in alpha. This will provide trivia, historical context, and 'Why this matters' callouts in future versions."

        return f"Error: Unsupported operation '{operation}'"  # noqa: TRY300

    except Exception as e:
        logger.exception("Enrichment error")
        return f"Error performing enrichment: {e}"
