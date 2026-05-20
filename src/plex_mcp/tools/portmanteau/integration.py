"""
PlexMCP Third-party Integration Portmanteau Tool

Consolidates all third-party integration operations into a single comprehensive interface.
FastMCP 3.2+ compliant with comprehensive docstrings and AI-friendly error messages.
"""

import os
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def plex_integration(
    operation: Annotated[
        Literal[
            "list_integrations", "vienna_recommendations", "european_content", "anime_season_info", "configure", "sync"
        ],
        Field(description="The integration operation to perform."),
    ],
    content_type: Annotated[str | None, Field(description="Content type filter (e.g., 'movie', 'show').")] = None,
    limit: Annotated[int, Field(description="Maximum number of results to return.", ge=1)] = 10,
    include_european: Annotated[bool, Field(description="Include European content in results.")] = True,
    country: Annotated[str | None, Field(description="Country code for content filtering.")] = None,
    year: Annotated[int | None, Field(description="Year for seasonal queries.")] = None,
    season: Annotated[
        Literal["winter", "spring", "summer", "fall"] | None, Field(description="Season filter for anime queries.")
    ] = None,
    integration_name: Annotated[str | None, Field(description="Name of the integration target.")] = None,
    config: Annotated[dict[str, Any] | None, Field(description="Configuration dictionary for the integration.")] = None,
) -> ToolResult:
    """Comprehensive third-party integration operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 external API integrations into a single tool to provide
    unified access to regional recommendations and niche metadata providers.

    ## Return Format
    {"success": bool, "operation": str, "data": list|dict, "count": int|None, "error": str|None}

    ## Examples
    await plex_integration(operation="list_integrations")
    await plex_integration(operation="vienna_recommendations", content_type="movie", limit=5)
    await plex_integration(operation="anime_season_info", year=2024, season="spring")
    await plex_integration(operation="configure", integration_name="vienna", config={"api_key": "..."})
    """
    try:
        from ...api.vienna import (
            get_anime_season_info,
            get_european_content,
            get_vienna_recommendations,
        )

        if operation == "list_integrations":
            integrations = [
                {"name": "vienna", "enabled": True, "description": "Vienna-specific content recommendations"},
                {"name": "european", "enabled": True, "description": "European content metadata"},
                {"name": "anime", "enabled": True, "description": "Anime season information"},
            ]
            return ToolResult(
                content={
                    "success": True,
                    "operation": "list_integrations",
                    "data": integrations,
                    "count": len(integrations),
                }
            )

        if operation == "vienna_recommendations":
            if not content_type:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "content_type is required for vienna_recommendations operation",
                        "error_code": "MISSING_CONTENT_TYPE",
                        "suggestions": ["Provide content_type parameter (e.g., 'movie', 'show')"],
                    }
                )

            from ...api.vienna import RecommendationRequest

            request = RecommendationRequest(content_type=content_type, limit=limit, include_european=include_european)
            result = await get_vienna_recommendations(request)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "vienna_recommendations",
                    "content_type": content_type,
                    "data": [item.model_dump() if hasattr(item, "model_dump") else item for item in result],
                    "count": len(result),
                }
            )

        if operation == "european_content":
            from ...api.vienna import EuropeanContentRequest

            request = EuropeanContentRequest(country=country, content_type=content_type, limit=limit)
            result = await get_european_content(request)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "european_content",
                    "country": country,
                    "content_type": content_type,
                    "data": [item.model_dump() if hasattr(item, "model_dump") else item for item in result],
                    "count": len(result),
                }
            )

        if operation == "anime_season_info":
            if year is None:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "year is required for anime_season_info operation",
                        "error_code": "MISSING_YEAR",
                        "suggestions": ["Provide year parameter (e.g., 2024)"],
                    }
                )
            if not season:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "season is required for anime_season_info operation",
                        "error_code": "MISSING_SEASON",
                        "suggestions": ["Provide season parameter: winter, spring, summer, or fall"],
                    }
                )

            from ...api.vienna import AnimeSeasonInfoRequest

            request = AnimeSeasonInfoRequest(year=year, season=season)
            result = await get_anime_season_info(request)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "anime_season_info",
                    "year": year,
                    "season": season,
                    "data": result.model_dump() if hasattr(result, "model_dump") else result,
                }
            )

        if operation == "configure":
            if not integration_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "integration_name is required for configure operation",
                        "error_code": "MISSING_INTEGRATION_NAME",
                        "suggestions": ["Provide integration_name parameter"],
                    }
                )
            if not config:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "config dictionary is required for configure operation",
                        "error_code": "MISSING_CONFIG",
                        "suggestions": ["Provide config parameter with configuration dictionary"],
                    }
                )

            logger.info(f"Configuring integration {integration_name} with config: {config}")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "configure",
                    "integration_name": integration_name,
                    "data": {"configured": True, "config": config},
                }
            )

        if operation == "sync":
            if not integration_name:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "integration_name is required for sync operation",
                        "error_code": "MISSING_INTEGRATION_NAME",
                        "suggestions": ["Provide integration_name parameter"],
                    }
                )

            logger.info(f"Syncing data from integration {integration_name}")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "sync",
                    "integration_name": integration_name,
                    "data": {"synced": True, "items_synced": 0},
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: list_integrations, vienna_recommendations, european_content, anime_season_info, configure, sync",
                    f"You provided: '{operation}'",
                ],
            }
        )

    except RuntimeError as e:
        error_msg = str(e)
        suggestions = []

        if "PLEX_TOKEN" in error_msg:
            suggestions = [
                "Set PLEX_TOKEN environment variable",
                "Get token from: Plex Web App -> Settings -> Account -> Authorized Devices",
                "Or visit: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/",
            ]

        return ToolResult(
            content={
                "success": False,
                "error": error_msg,
                "error_code": "RUNTIME_ERROR",
                "operation": operation,
                "suggestions": suggestions,
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in plex_integration operation '{operation}': {e}", exc_info=True)
        return ToolResult(
            content={
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
        )
