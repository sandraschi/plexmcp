"""
PlexMCP Third-party Integration Portmanteau Tool

Consolidates all third-party integration operations into a single comprehensive interface.
FastMCP 2.13+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Any, Literal

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)


def _get_plex_service():
    """Get PlexService instance with proper environment variable handling."""
    from ...services.plex_service import PlexService

    base_url = os.getenv("PLEX_URL") or os.getenv("PLEX_SERVER_URL", "http://localhost:32400")
    token = os.getenv("PLEX_TOKEN")

    if not token:
        raise RuntimeError(
            "PLEX_TOKEN environment variable is required. "
            "Get your token from Plex Web App (Settings -> Account -> Authorized Devices) "
            "or visit https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ "
            "for detailed instructions."
        )

    return PlexService(base_url=base_url, token=token)


@mcp.tool()
async def plex_integration(
    operation: Literal[
        "list_integrations",
        "vienna_recommendations",
        "european_content",
        "anime_season_info",
        "configure",
        "sync",
    ],
    content_type: str | None = None,
    limit: int = 10,
    include_european: bool = True,
    country: str | None = None,
    year: int | None = None,
    season: Literal["winter", "spring", "summer", "fall"] | None = None,
    integration_name: str | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Comprehensive third-party integration operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 external API integrations into a single tool to provide
    unified access to regional recommendations and niche metadata providers.

    OPERATIONS:
    - list_integrations: Audit all active and available external service bridges.
    - vienna_recommendations: Specialized Alsergrund-tuned local content suggestions.
    - european_content: Filter for EU-origin media with localized Vienna metadata.
    - anime_season_info: Retrieval of seasonal metadata from specialized anime databases.
    - configure: Manage API keys and synchronization preferences for integrations.
    - sync: Trigger a manual state refresh from an external provider.

    Returns:
    FastMCP 3.1+ dialogic response with external metadata and integration status.
    Enables autonomous regional content curation and seasonal discovery.
    """
    try:
        # Import Vienna API functions
        from ...api.vienna import (
            get_anime_season_info,
            get_european_content,
            get_vienna_recommendations,
        )

        # Operation: list_integrations
        if operation == "list_integrations":
            # Placeholder - would list available integrations
            integrations = [
                {
                    "name": "vienna",
                    "enabled": True,
                    "description": "Vienna-specific content recommendations",
                },
                {
                    "name": "european",
                    "enabled": True,
                    "description": "European content metadata",
                },
                {
                    "name": "anime",
                    "enabled": True,
                    "description": "Anime season information",
                },
            ]
            return {
                "success": True,
                "operation": "list_integrations",
                "data": integrations,
                "count": len(integrations),
            }

        # Operation: vienna_recommendations
        if operation == "vienna_recommendations":
            if not content_type:
                return {
                    "success": False,
                    "error": "content_type is required for vienna_recommendations operation",
                    "error_code": "MISSING_CONTENT_TYPE",
                    "suggestions": ["Provide content_type parameter (e.g., 'movie', 'show')"],
                }

            from ...api.vienna import RecommendationRequest

            request = RecommendationRequest(
                content_type=content_type,
                limit=limit,
                include_european=include_european,
            )
            result = await get_vienna_recommendations(request)
            return {
                "success": True,
                "operation": "vienna_recommendations",
                "content_type": content_type,
                "data": [item.dict() if hasattr(item, "dict") else item for item in result],
                "count": len(result),
            }

        # Operation: european_content
        if operation == "european_content":
            from ...api.vienna import EuropeanContentRequest

            request = EuropeanContentRequest(country=country, content_type=content_type, limit=limit)
            result = await get_european_content(request)
            return {
                "success": True,
                "operation": "european_content",
                "country": country,
                "content_type": content_type,
                "data": [item.dict() if hasattr(item, "dict") else item for item in result],
                "count": len(result),
            }

        # Operation: anime_season_info
        if operation == "anime_season_info":
            if year is None:
                return {
                    "success": False,
                    "error": "year is required for anime_season_info operation",
                    "error_code": "MISSING_YEAR",
                    "suggestions": ["Provide year parameter (e.g., 2024)"],
                }
            if not season:
                return {
                    "success": False,
                    "error": "season is required for anime_season_info operation",
                    "error_code": "MISSING_SEASON",
                    "suggestions": ["Provide season parameter: winter, spring, summer, or fall"],
                }

            from ...api.vienna import AnimeSeasonInfoRequest

            request = AnimeSeasonInfoRequest(year=year, season=season)
            result = await get_anime_season_info(request)
            return {
                "success": True,
                "operation": "anime_season_info",
                "year": year,
                "season": season,
                "data": result.dict() if hasattr(result, "dict") else result,
            }

        # Operation: configure
        if operation == "configure":
            if not integration_name:
                return {
                    "success": False,
                    "error": "integration_name is required for configure operation",
                    "error_code": "MISSING_INTEGRATION_NAME",
                    "suggestions": ["Provide integration_name parameter"],
                }
            if not config:
                return {
                    "success": False,
                    "error": "config dictionary is required for configure operation",
                    "error_code": "MISSING_CONFIG",
                    "suggestions": ["Provide config parameter with configuration dictionary"],
                }

            # Placeholder implementation
            logger.info(f"Configuring integration {integration_name} with config: {config}")
            return {
                "success": True,
                "operation": "configure",
                "integration_name": integration_name,
                "data": {"configured": True, "config": config},
            }

        # Operation: sync
        if operation == "sync":
            if not integration_name:
                return {
                    "success": False,
                    "error": "integration_name is required for sync operation",
                    "error_code": "MISSING_INTEGRATION_NAME",
                    "suggestions": ["Provide integration_name parameter"],
                }

            # Placeholder implementation
            logger.info(f"Syncing data from integration {integration_name}")
            return {
                "success": True,
                "operation": "sync",
                "integration_name": integration_name,
                "data": {"synced": True, "items_synced": 0},  # Placeholder
            }

        return {
            "success": False,
            "error": f"Invalid operation: '{operation}'",
            "error_code": "INVALID_OPERATION",
            "suggestions": [
                "Valid operations: list_integrations, vienna_recommendations, european_content, anime_season_info, configure, sync",
                f"You provided: '{operation}'",
            ],
        }

    except RuntimeError as e:
        error_msg = str(e)
        suggestions = []

        if "PLEX_TOKEN" in error_msg:
            suggestions = [
                "Set PLEX_TOKEN environment variable",
                "Get token from: Plex Web App -> Settings -> Account -> Authorized Devices",
                "Or visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]

        return {
            "success": False,
            "error": error_msg,
            "error_code": "RUNTIME_ERROR",
            "operation": operation,
            "suggestions": suggestions,
        }

    except Exception as e:
        logger.error(
            f"Unexpected error in plex_integration operation '{operation}': {e}",
            exc_info=True,
        )
        return {
            "success": False,
            "error": f"Unexpected error during {operation}: {str(e)}",
            "error_code": "UNEXPECTED_ERROR",
            "operation": operation,
            "suggestions": [
                "Check server logs for detailed error information",
                "Verify all required parameters are provided",
                "Try the operation again with valid parameters",
            ],
        }
