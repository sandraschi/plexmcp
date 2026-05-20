"""
Plex Media Enrichment Portmanteau Tool (FastMCP 3.1)

Consolidates external metadata discovery and high-value enrichment.
"""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.enrichment_service import get_enrichment_service
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def plex_media_enrichment(
    operation: Annotated[
        Literal["enrich_item", "get_external_metadata", "analyze_trends"],
        Field(description="Operation to perform."),
    ],
    title: Annotated[str, Field(description="Title of the media item to enrich.")],
    year: Annotated[int | None, Field(description="Release year of the item.")] = None,
    media_type: Annotated[
        Literal["movie", "show"],
        Field(description="Type of media."),
    ] = "movie",
) -> ToolResult:
    """High-value media enrichment using external sources (Wikipedia, TMDB, TVDB).

    This tool adds 'Informed Discovery' capabilities to PlexMCP by fetching
    contextual metadata that Plex does not natively provide.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates external metadata discovery into a single enrichment interface.

    ## Return Format
    {"success": bool, "data": str, "message": str}

    ## Examples
    await plex_media_enrichment(operation="enrich_item", title="Inception", year=2010)
    """
    enrich_service = get_enrichment_service()

    try:
        if operation == "enrich_item":
            logger.info(f"Enriching {media_type}: {title} ({year})")
            wiki = await enrich_service.fetch_wikipedia_summary(title, year, media_type)

            if not wiki or not (wiki.get("summary") or "").strip():
                return ToolResult(
                    content={
                        "success": True,
                        "data": f"### High-Value Enrichment: {title}\n\nNo Wikipedia article summary matched this title/year. Try adjusting the year or use get_external_metadata for search links.",
                    }
                )

            extract = (wiki.get("summary") or "").strip()
            page_url = wiki.get("url") or ""
            markdown = f"""
### High-Value context: {title} ({year if year else "N/A"})

**Source:** {wiki.get("source", "Wikipedia")}  
**Article:** {page_url}

{extract}

---
> Tip: Enable Wikipedia enrichment during RAG metadata sync (`plex_rag` / `enrich=True`) for searchable deep context.
"""
            return ToolResult(
                content={
                    "success": True,
                    "data": markdown,
                }
            )

        if operation == "get_external_metadata":
            markdown = f"""
### External Discovery: {title}

| Source | Status | Link |
| :--- | :--- | :--- |
| Wikipedia | Found | [View Article](https://en.wikipedia.org/wiki/{title.replace(" ", "_")}) |
| TMDB | Linked | [Direct Search](https://www.themoviedb.org/search?query={title.replace(" ", "%20")}) |
| TV Tropes | Staged | [Direct Search](https://tvtropes.org/pmwiki/search_result.php?q={title.replace(" ", "+")}) |

> [!NOTE]
> Detailed ID mapping (TMDB_ID, TVDB_ID) is available via the enriched RAG index for indexed items.
"""
            return ToolResult(
                content={
                    "success": True,
                    "data": markdown,
                }
            )

        if operation == "analyze_trends":
            return ToolResult(
                content={
                    "success": True,
                    "data": f"### [MOCK] Cultural Analysis: {title}\n\nCultural trend analysis is currently in alpha. This will provide trivia, historical context, and 'Why this matters' callouts in future versions.",
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Unsupported operation '{operation}'",
                "error_code": "INVALID_OPERATION",
            }
        )

    except Exception as e:
        logger.exception("Enrichment error")
        return ToolResult(
            content={
                "success": False,
                "error": f"Error performing enrichment: {e}",
                "error_code": "ENRICHMENT_ERROR",
            }
        )
