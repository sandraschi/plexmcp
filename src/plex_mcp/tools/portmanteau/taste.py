"""
Plex Taste Portmanteau Tool (FastMCP 3.1)

Learns a taste profile from watch history and ranks items against it.
"""

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.taste import queries, sync
from ...utils import get_logger

logger = get_logger(__name__)


def _ok(operation: str, data: Any, message: str = "") -> ToolResult:
    return ToolResult(content={"success": True, "operation": operation, "data": data, "message": message})


def _err(operation: str, error: str, code: str, suggestions: list[str] | None = None) -> ToolResult:
    return ToolResult(
        content={
            "success": False,
            "operation": operation,
            "error": error,
            "error_code": code,
            "suggestions": suggestions or [],
        }
    )


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def plex_taste(
    operation: Annotated[
        Literal[
            "status",
            "rebuild_from_history",
            "sync",
            "profile",
            "temporal_profile",
            "recent_shifts",
            "dimensions_for",
            "score_item",
            "score_library",
        ],
        Field(description="Operation to perform."),
    ],
    kind: Annotated[
        Literal["movie", "show"],
        Field(description="Movies and TV are scored separately; they are different populations."),
    ] = "movie",
    rating_key: Annotated[str | None, Field(description="Plex rating key (dimensions_for, score_item).")] = None,
    library_id: Annotated[str | None, Field(description="Movie or show library to rank (score_library).")] = None,
    time_bucket: Annotated[
        str | None,
        Field(
            description="Restrict to a time of week: weekday_morning, weekday_afternoon, weekday_evening, "
            "saturday_morning, sunday_morning, weekend_afternoon, weekend_evening, late_night."
        ),
    ] = None,
    top: Annotated[int, Field(description="Max likes and max dislikes to return.", ge=1, le=200)] = 25,
    prefix: Annotated[
        str | None, Field(description="Only one dimension family: genre, director, actor, decade, country, runtime.")
    ] = None,
    days: Annotated[int, Field(description="Window for recent_shifts.", ge=1, le=365)] = 30,
    limit: Annotated[int, Field(description="Max items for score_library.", ge=1, le=500)] = 50,
    unwatched_only: Annotated[bool, Field(description="score_library: skip items already watched.")] = True,
    refresh_baseline: Annotated[
        bool, Field(description="rebuild_from_history: re-survey the whole library (adds ~1-2 minutes).")
    ] = False,
) -> ToolResult:
    """Taste profile learned from your Plex watch history, and taste-fit ranking of items.

    A dimension's score is LIFT against your library, in [-1, 1]: how much more (+) or
    less (-) attention it gets than its share of what's available. 0 means proportional;
    -1 means plentiful in the library but never watched. Recent history counts more
    (1-year half-life). Movies and TV are scored separately.

    Signals: a history entry is a completed view, a repeat view is a rewatch, ratings of
    4+ stars / 2- stars count strongly, and partly-watched-then-left items count as a
    dampened negative. Plex does not expose "dismissed from On Deck", so that is not captured.

    Start with rebuild_from_history (a few minutes on a large library), then profile.

    ## Return Format
    {"success": bool, "operation": str, "data": ..., "message": str}

    ## Examples
    await plex_taste(operation="rebuild_from_history")
    await plex_taste(operation="profile", kind="movie", prefix="director", top=10)
    await plex_taste(operation="temporal_profile", time_bucket="sunday_morning", kind="movie")
    await plex_taste(operation="score_item", rating_key="12345")
    await plex_taste(operation="score_library", library_id="1", limit=20)
    await plex_taste(operation="recent_shifts", days=30)
    """
    try:
        if operation == "status":
            return _ok(operation, sync.status())

        if operation in ("rebuild_from_history", "sync"):
            if sync.is_running():
                return _err(operation, "A taste sync is already running.", "ALREADY_RUNNING")
            server = await sync.get_plex_server()
            if operation == "sync":
                result = await sync.sync(server)
            else:
                result = await sync.rebuild_from_history(server, refresh_baseline=refresh_baseline)
            return _ok(operation, result)

        if operation == "profile":
            return _ok(operation, queries.get_profile(kind, time_bucket, top, prefix))

        if operation == "temporal_profile":
            if not time_bucket:
                return _err(
                    operation,
                    "time_bucket is required",
                    "MISSING_TIME_BUCKET",
                    ["Example: time_bucket='sunday_morning'"],
                )
            return _ok(operation, queries.get_profile(kind, time_bucket, top, prefix))

        if operation == "recent_shifts":
            shifts = queries.get_recent_shifts(kind, days, top, prefix)
            return _ok(operation, shifts, f"{len(shifts)} dimension(s) shifted in the last {days} days.")

        if operation in ("dimensions_for", "score_item"):
            if not rating_key:
                return _err(operation, "rating_key is required", "MISSING_RATING_KEY")
            if operation == "dimensions_for":
                return _ok(operation, await queries.dimensions_for(rating_key))
            return _ok(operation, await queries.score_item(rating_key, time_bucket))

        if operation == "score_library":
            if not library_id:
                return _err(
                    operation,
                    "library_id is required",
                    "MISSING_LIBRARY_ID",
                    ["Use plex_library(operation='list') to find library ids"],
                )
            return _ok(operation, await queries.score_library(library_id, None, limit, unwatched_only, time_bucket))

        return _err(operation, f"Unsupported operation '{operation}'", "INVALID_OPERATION")

    except queries.TasteNotBuilt as e:
        return _err(operation, str(e), "NOT_BUILT", ["Run plex_taste(operation='rebuild_from_history')"])
    except (ValueError, LookupError) as e:
        return _err(operation, str(e), "INVALID_INPUT")
    except RuntimeError as e:
        return _err(operation, str(e), "PLEX_NOT_CONFIGURED")
    except Exception as e:
        logger.exception("plex_taste failed")
        return _err(operation, f"Taste operation failed: {e}", "TASTE_ERROR")
