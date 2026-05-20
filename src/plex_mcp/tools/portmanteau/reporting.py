"""
PlexMCP Reporting & Analytics Portmanteau Tool

Consolidates all reporting and analytics operations into a single comprehensive interface.
FastMCP 3.2 compliant.
"""

import os
from typing import Annotated, Literal

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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def plex_reporting(
    operation: Annotated[
        Literal[
            "library_stats",
            "usage_report",
            "content_report",
            "user_activity",
            "performance_report",
            "export_report",
        ],
        Field(description="Reporting operation to execute."),
    ],
    library_id: Annotated[str | None, Field(description="Target library ID for scoped reports.")] = None,
    time_range: Annotated[str | None, Field(description="Time range filter (e.g. '7d', '30d', 'all').")] = None,
    format: Annotated[
        Literal["json", "csv", "html"] | None, Field(description="Export format for export_report operation.")
    ] = None,
    output_path: Annotated[str | None, Field(description="File path for export_report output.")] = None,
) -> ToolResult:
    """
    Comprehensive reporting and analytics tool for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 6 reporting and server diagnostic operations into a single tool to provide
    a systematic overview of library growth and server health.

    ## Return Format
    ToolResult with content dict: {"success": bool, "operation": str, "stats"/"reports"/"server_status": ...}

    ## Examples
    await plex_reporting(operation="library_stats")
    await plex_reporting(operation="performance_report")
    await plex_reporting(operation="library_stats", library_id="1")
    """
    try:
        plex = _get_plex_service()

        if operation == "library_stats":
            if library_id:
                libraries = await plex.get_library(library_id)
                if not libraries:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": f"Library with ID '{library_id}' not found",
                            "error_code": "LIBRARY_NOT_FOUND",
                            "suggestions": [
                                "Verify library_id is correct",
                                "List libraries to see available IDs",
                            ],
                        }
                    )
                libraries = [libraries]
            else:
                libraries = await plex.list_libraries()

            stats = []
            for lib in libraries:
                lib_id = lib.get("key") or lib.get("id")
                analysis = await plex.analyze_library(lib_id)
                stats.append(
                    {
                        "library_id": lib_id,
                        "library_name": lib.get("title") or lib.get("name"),
                        "total_items": analysis.get("total_items", 0),
                        "issues_found": analysis.get("issues_found", 0),
                        "issues": analysis.get("issues", []),
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "library_stats",
                    "stats": stats,
                    "count": len(stats),
                }
            )

        if operation == "usage_report":
            return ToolResult(
                content={
                    "success": True,
                    "operation": "usage_report",
                    "time_range": time_range or "all",
                    "message": "[SIMULATED] Usage reporting requires session history data (not yet implemented)",
                    "data": {},
                }
            )

        if operation == "content_report":
            if library_id:
                libraries = await plex.get_library(library_id)
                if not libraries:
                    return ToolResult(
                        content={
                            "success": False,
                            "error": f"Library with ID '{library_id}' not found",
                            "error_code": "LIBRARY_NOT_FOUND",
                        }
                    )
                libraries = [libraries]
            else:
                libraries = await plex.list_libraries()

            reports = []
            for lib in libraries:
                lib_id = lib.get("key") or lib.get("id")
                items_result = await plex.get_library_items(library_id=lib_id, limit=1000, offset=0)
                items = items_result.get("items", []) if isinstance(items_result, dict) else items_result
                reports.append(
                    {
                        "library_id": lib_id,
                        "library_name": lib.get("title") or lib.get("name"),
                        "total_items": len(items) if isinstance(items, list) else items_result.get("total", 0),
                        "content_types": {},
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "content_report",
                    "reports": reports,
                    "count": len(reports),
                }
            )

        if operation == "user_activity":
            return ToolResult(
                content={
                    "success": True,
                    "operation": "user_activity",
                    "time_range": time_range or "all",
                    "message": "[SIMULATED] User activity reporting requires session history data (not yet implemented)",
                    "data": {},
                }
            )

        if operation == "performance_report":
            status = await plex.get_server_status()
            return ToolResult(
                content={
                    "success": True,
                    "operation": "performance_report",
                    "server_status": status.model_dump() if hasattr(status, "model_dump") else status,
                    "recommendations": [],
                }
            )

        if operation == "export_report":
            if not format:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "format is required for export_report operation",
                        "error_code": "MISSING_PARAMETER",
                        "suggestions": ["Specify format: json, csv, or html"],
                    }
                )

            return ToolResult(
                content={
                    "success": True,
                    "operation": "export_report",
                    "format": format,
                    "output_path": output_path,
                    "message": f"[SIMULATED] Report export to {format} format (not yet fully implemented)",
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Unknown operation: {operation}",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Use one of: library_stats, usage_report, content_report, user_activity, performance_report, export_report"
                ],
            }
        )

    except Exception as e:
        logger.error(f"Error in plex_reporting operation '{operation}': {e}", exc_info=True)
        return ToolResult(
            content={
                "success": False,
                "error": str(e),
                "error_code": "EXECUTION_ERROR",
                "suggestions": [
                    "Verify Plex server is accessible",
                    "Check PLEX_TOKEN is set correctly",
                    "Verify library_id is valid if provided",
                ],
            }
        )
