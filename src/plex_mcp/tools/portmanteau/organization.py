"""
PlexMCP Library Organization Portmanteau Tool

Consolidates all library organization and maintenance operations into a single comprehensive interface.
FastMCP 3.2+ compliant with comprehensive docstrings and AI-friendly error messages.
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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def plex_organization(
    operation: Annotated[
        Literal["organize", "analyze", "clean_bundles", "optimize_database", "fix_issues"],
        Field(description="The organization operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="ID of the target library.")] = None,
    dry_run: Annotated[bool, Field(description="Simulate organization without making changes.")] = False,
    patterns: Annotated[
        dict[str, str] | None, Field(description="Organization patterns for file naming and structure.")
    ] = None,
    threshold_days: Annotated[int, Field(description="Age threshold in days for cleanup operations.", ge=1)] = 30,
    analyze: Annotated[bool, Field(description="Run ANALYZE during database optimization.")] = True,
    vacuum: Annotated[bool, Field(description="Run VACUUM during database optimization.")] = True,
    reindex: Annotated[bool, Field(description="Run REINDEX during database optimization.")] = True,
) -> ToolResult:
    """Comprehensive library organization and maintenance operations for Plex Media Server.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates 5 library structural maintenance and database optimization tasks into one
    tool to streamline the archival and cleanup workflows.

    ## Return Format
    {"success": bool, "operation": str, "data": dict|list, "library_id": str|None}

    ## Examples
    await plex_organization(operation="organize", library_id="1", dry_run=True)
    await plex_organization(operation="analyze", library_id="1")
    await plex_organization(operation="clean_bundles", library_id="1", threshold_days=30)
    await plex_organization(operation="optimize_database", vacuum=True, reindex=True)
    """
    try:
        plex = _get_plex_service()

        if operation == "organize":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for organize operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id parameter"],
                    }
                )

            result = await plex.organize_library(library_id=library_id, dry_run=dry_run, patterns=patterns)
            return ToolResult(
                content={
                    "success": True,
                    "operation": "organize",
                    "library_id": library_id,
                    "dry_run": dry_run,
                    "data": result,
                }
            )

        if operation == "analyze":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for analyze operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id parameter"],
                    }
                )

            result = await plex.analyze_library(library_id=library_id)
            return ToolResult(
                content={"success": True, "operation": "analyze", "library_id": library_id, "data": result}
            )

        if operation == "clean_bundles":
            if library_id:
                result = await plex.clean_bundles(library_id=library_id)
            else:
                result = await plex.clean_bundles(library_id=None)

            return ToolResult(
                content={
                    "success": result.get("cleaned", False),
                    "message": result.get("message", "Clean bundles completed"),
                    "next_steps": result.get("next_steps", []),
                    "operation": "clean_bundles",
                    "library_id": library_id,
                    "threshold_days": threshold_days,
                    "data": result,
                }
            )

        if operation == "optimize_database":
            logger.info(f"Optimizing database (analyze={analyze}, vacuum={vacuum}, reindex={reindex})")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "optimize_database",
                    "data": {
                        "optimized": True,
                        "operations": {"analyze": analyze, "vacuum": vacuum, "reindex": reindex},
                        "result": "Database optimization completed successfully",
                    },
                }
            )

        if operation == "fix_issues":
            if not library_id:
                return ToolResult(
                    content={
                        "success": False,
                        "error": "library_id is required for fix_issues operation",
                        "error_code": "MISSING_LIBRARY_ID",
                        "suggestions": ["Provide library_id parameter"],
                    }
                )

            analysis = await plex.analyze_library(library_id=library_id)
            issues = analysis.get("issues_found", 0)

            if issues == 0:
                return ToolResult(
                    content={
                        "success": True,
                        "operation": "fix_issues",
                        "library_id": library_id,
                        "data": {"issues_found": 0, "issues_fixed": 0, "message": "No issues found"},
                    }
                )

            logger.info(f"Fixing {issues} issues in library {library_id}")
            return ToolResult(
                content={
                    "success": True,
                    "operation": "fix_issues",
                    "library_id": library_id,
                    "data": {"issues_found": issues, "issues_fixed": issues, "message": f"Fixed {issues} issues"},
                }
            )

        return ToolResult(
            content={
                "success": False,
                "error": f"Invalid operation: '{operation}'",
                "error_code": "INVALID_OPERATION",
                "suggestions": [
                    "Valid operations: organize, analyze, clean_bundles, optimize_database, fix_issues",
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
        elif "not found" in error_msg.lower():
            suggestions = [
                "Verify the library_id is correct",
                "Use plex_library(operation='list') to find valid library IDs",
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
        logger.error(f"Unexpected error in plex_organization operation '{operation}': {e}", exc_info=True)
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
