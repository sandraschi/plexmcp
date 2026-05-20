from typing import Any

import httpx

from ..utils import get_logger

logger = get_logger(__name__)


class MediaEnrichmentService:
    """Service for fetching external high-value metadata about media items."""

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

    async def close(self):
        await self.http_client.aclose()

    async def enrich_media(self, title: str, year: int | None = None, media_type: str = "movie") -> dict[str, Any]:
        """Fetch enrichment data from Wikipedia and other sources."""
        return {"wikipedia": await self.fetch_wikipedia_summary(title, year, media_type), "external_sources": []}

        # In a real implementation, we would add TMDB/TVDB search here.
        # For SOTA 2026, we prioritize Wikipedia for its high-quality narrative context.

    async def fetch_wikipedia_summary(
        self, title: str, year: int | None = None, media_type: str = "movie"
    ) -> dict[str, Any] | None:
        """Fetch a summary from Wikipedia REST API."""
        try:
            # Try with year first for better precision
            search_title = f"{title} ({year} film)" if year and media_type == "movie" else title
            formatted_title = search_title.replace(" ", "_")
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"

            response = await self.http_client.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "Wikipedia",
                    "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    "summary": data.get("extract", ""),
                    "description": data.get("description", ""),
                    "thumbnail": data.get("thumbnail", {}).get("source", ""),
                }

            # Fallback to plain title
            if search_title != title:
                formatted_title = title.replace(" ", "_")
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"
                response = await self.http_client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "source": "Wikipedia",
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "summary": data.get("extract", ""),
                        "description": data.get("description", ""),
                        "thumbnail": data.get("thumbnail", {}).get("source", ""),
                    }

            return None
        except Exception as e:
            logger.exception(f"Error fetching Wikipedia summary for {title}: {e}")
            return None


# Global instance
_enrichment_service = None


def get_enrichment_service() -> MediaEnrichmentService:
    global _enrichment_service
    if _enrichment_service is None:
        _enrichment_service = MediaEnrichmentService()
    return _enrichment_service
