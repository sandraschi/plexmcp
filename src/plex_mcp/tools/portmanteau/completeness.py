"""
Plex Completeness Portmanteau Tool (gap-in-library detection).

Ports CalibreMCP's series-gap analysis to TV: answers "which shows are
missing episodes?" by walking show -> seasons -> episodes and diffing each
season's held episode numbers against the expected 1..max range.

Honest limit (same as the Calibre original): Plex only knows what it holds,
so the expected range is 1..highest-held per season. Episodes beyond the
highest held (unaired, never ripped) are invisible to this tool — it finds
holes *inside* your holdings, not titles you never owned.
"""

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)

_CHILD_LIMIT = 500


def _get_plex_service():
    """Get PlexService instance with proper environment variable handling."""
    from ...config import get_settings
    from ...services.plex_service import PlexService

    settings = get_settings()

    if not settings.plex_token:
        raise RuntimeError(
            "PLEX_TOKEN environment variable is required. "
            "Get your token from Plex Web App (Settings > Account > Authorized Devices) "
            "or visit https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/ "
            "for detailed instructions."
        )

    return PlexService(base_url=settings.server_url, token=settings.plex_token, timeout=settings.timeout)


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


def _num(value: Any) -> int | None:
    """Coerce Plex index fields (int, numeric str) to int; else None."""
    try:
        if value is None or value is True or value is False:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _gap_ranges(season_no: int, missing: list[int]) -> list[str]:
    """Collapse missing episode numbers to SxxEyy ranges (Calibre #a-#b style)."""
    ranges: list[str] = []
    if not missing:
        return ranges
    start = prev = missing[0]
    for n in missing[1:]:
        if n == prev + 1:
            prev = n
        else:
            ranges.append(
                f"S{season_no:02d}E{start:02d}" if start == prev else f"S{season_no:02d}E{start:02d}-E{prev:02d}"
            )
            start = prev = n
    ranges.append(f"S{season_no:02d}E{start:02d}" if start == prev else f"S{season_no:02d}E{start:02d}-E{prev:02d}")
    return ranges


async def _season_gaps(plex, show_id: str, show_title: str) -> dict[str, Any]:
    """Walk one show's seasons; return per-season gaps + rollup."""
    kids = await plex.get_media_children(show_id, limit=_CHILD_LIMIT)
    seasons = [c for c in (kids.get("items") or []) if c.get("type") == "season"]
    season_reports: list[dict[str, Any]] = []
    missing_total = 0
    held_total = 0
    expected_total = 0
    for s in seasons:
        season_no = _num(s.get("index"))
        if season_no is None:
            continue
        eks = await plex.get_media_children(s.get("id") or s.get("rating_key"), limit=_CHILD_LIMIT)
        ep_nums = sorted(
            {
                n
                for e in (eks.get("items") or [])
                if e.get("type") == "episode" and (n := _num(e.get("index"))) is not None
            }
        )
        if not ep_nums:
            continue
        expected = list(range(1, ep_nums[-1] + 1))
        missing = [n for n in expected if n not in set(ep_nums)]
        held_total += len(ep_nums)
        expected_total += len(expected)
        missing_total += len(missing)
        season_reports.append(
            {
                "season": season_no,
                "season_title": s.get("title"),
                "held": len(ep_nums),
                "expected": len(expected),
                "missing": missing,
                "gaps": _gap_ranges(season_no, missing),
            }
        )
    completion = round(held_total / expected_total * 100, 1) if expected_total else 100.0
    return {
        "show_id": str(show_id),
        "show_title": show_title,
        "seasons_held": len(season_reports),
        "episodes_held": held_total,
        "episodes_expected": expected_total,
        "missing_count": missing_total,
        "completion_percent": completion,
        "complete": missing_total == 0,
        "seasons": season_reports,
    }


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def plex_completeness(
    operation: Annotated[
        Literal["status", "scan_library", "show_gaps"],
        Field(description="The completeness operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="Show library section id (scan_library).")] = None,
    rating_key: Annotated[str | None, Field(description="Show rating key (show_gaps).")] = None,
    max_shows: Annotated[int, Field(description="Max shows to deep-walk in scan_library (latency cap).")] = 25,
    include_complete: Annotated[bool, Field(description="Include complete shows in scan_library output.")] = False,
) -> ToolResult:
    """
    Systematic gap-in-library detection for TV libraries.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates show inventory, library-wide gap scans, and single-show
    depth checks into one tool so "what am I missing?" is one call chain.

    OPERATIONS:
    - status: show-library inventory (sections + show counts, no deep walk).
    - scan_library: per-show season/episode gaps for a show library
      (worst-first, capped by max_shows).
    - show_gaps: full-depth gap report for one show rating_key.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    await plex_completeness(operation="status")
    await plex_completeness(operation="scan_library", library_id="2")
    await plex_completeness(operation="show_gaps", rating_key="12345")
    """
    try:
        plex = _get_plex_service()

        if operation == "status":
            libs = await plex.get_libraries()
            show_libs = []
            total_shows = 0
            for lib in libs or []:
                if lib.get("type") != "show":
                    continue
                lib_id = lib.get("id")
                if not lib_id:
                    continue
                items = await plex.get_library_items(library_id=str(lib_id), libtype="show", limit=1)
                count = items.get("total", 0) if isinstance(items, dict) else 0
                total_shows += count
                show_libs.append({"id": lib.get("id"), "title": lib.get("title"), "show_count": count})
            return _ok(
                operation,
                {"show_libraries": show_libs, "total_shows": total_shows},
                f"{total_shows} shows across {len(show_libs)} TV librar{'y' if len(show_libs) == 1 else 'ies'}.",
            )

        if operation == "scan_library":
            if not library_id:
                return _err(
                    operation,
                    "library_id is required for scan_library.",
                    "MISSING_PARAMETER",
                    ["Use status to list show libraries first"],
                )
            items = await plex.get_library_items(library_id=library_id, libtype="show", limit=500)
            shows = items.get("items", []) if isinstance(items, dict) else []
            truncated = len(shows) > max_shows
            reports = []
            for s in shows[:max_shows]:
                try:
                    reports.append(
                        await _season_gaps(plex, s.get("id") or s.get("rating_key"), s.get("title", "Unknown"))
                    )
                except Exception as e:
                    logger.warning("Gap walk failed for show %r: %s", s.get("title"), e)
            reports.sort(key=lambda r: r["missing_count"], reverse=True)
            if not include_complete:
                reports = [r for r in reports if not r["complete"]]
            missing_total = sum(r["missing_count"] for r in reports)
            return _ok(
                operation,
                {
                    "library_id": library_id,
                    "shows_scanned": min(len(shows), max_shows),
                    "shows_total": len(shows),
                    "truncated": truncated,
                    "shows_with_gaps": sum(1 for r in reports if not r["complete"]),
                    "total_missing_episodes": missing_total,
                    "shows": reports,
                },
                f"{missing_total} missing episodes across {sum(1 for r in reports if not r['complete'])} gappy shows"
                + (" (list truncated — raise max_shows for the rest)." if truncated else "."),
            )

        if operation == "show_gaps":
            if not rating_key:
                return _err(
                    operation,
                    "rating_key is required for show_gaps.",
                    "MISSING_PARAMETER",
                    ["Find the show via plex_search first"],
                )
            meta = await plex.get_media_metadata(rating_key)
            title = (meta or {}).get("title", rating_key) if isinstance(meta, dict) else rating_key
            report = await _season_gaps(plex, rating_key, str(title))
            return _ok(
                operation,
                report,
                f"{title}: {report['missing_count']} missing episodes ({report['completion_percent']}% complete).",
            )

        return _err(
            operation,
            f"Unknown operation: {operation}.",
            "INVALID_OPERATION",
            ["Use status, scan_library, or show_gaps"],
        )
    except Exception as e:
        logger.error("Error in plex_completeness operation '%s': %s", operation, e, exc_info=True)
        return _err(operation, str(e), "EXECUTION_ERROR")
