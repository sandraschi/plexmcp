"""
Plex Canon Portmanteau Tool (holdings vs canon lists).

Ports CalibreMCP's canon_coverage to film and TV: answers "what canonical
movies/shows am I missing?" by checking Plex holdings against canon lists.
All list data is either fetched live from real sources or supplied by the
caller — nothing is hardcoded from memory:

- oscar_best_picture: live Wikipedia Academy-Award-for-Best-Picture decade
  tables (bold == winner, year tracked across rowspans), title+year matching.
- afi_100: live Wikipedia AFI 100 Years...100 Movies table (2007 ranks),
  title+year matching.
- tmdb_top: live TMDB top_rated (movies and/or TV, needs TMDB_API_KEY).
- check_list: caller-supplied [{title, year?}] — e.g. an LLM-generated
  1001-Movies slice, a Sight & Sound ballot, a book appendix. No invention,
  just matching. This is the slot for book/article/website canons with no
  single stable live table (the 1001 Movies book itself included).
- list_canons: enumerate the available canons (no network).
"""

import os
import re
import urllib.request
from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)

AFI_URL = "https://en.wikipedia.org/wiki/AFI%27s_100_Years...100_Movies"
OSCARS_URL = "https://en.wikipedia.org/wiki/Academy_Award_for_Best_Picture"
TMDB_BASE = "https://api.themoviedb.org/3"
NETWORK_TIMEOUT = 25
_MAX_CHECK_ITEMS = 200


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


def _norm(s: Any) -> str:
    """Lowercase alphanumeric fingerprint for fuzzy title matching."""
    return re.sub(r"[^a-z0-9]+", " ", str(s or "").lower()).strip()


def _titles_match(canon_title: str, lib_title: Any) -> bool:
    """Containment either way, with a minimum-length guard against 'It'/'Up' hits."""
    c, lb = _norm(canon_title), _norm(lib_title)
    if len(c) < 4 or len(lb) < 4:
        return False
    return c in lb or lb in c


def _year_ok(canon_year: Any, lib_year: Any) -> bool:
    """Year gate (+-1): Plex holdings carry years, unlike books — use them."""
    try:
        if canon_year is None or lib_year is None:
            return True
        return abs(int(canon_year) - int(lib_year)) <= 1
    except (TypeError, ValueError):
        return True


def _item_title(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("title") or "")
    return str(getattr(item, "title", "") or "")


def _item_year(item: Any) -> Any:
    if isinstance(item, dict):
        return item.get("year")
    return getattr(item, "year", None)


def _item_type(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("type") or "")
    return str(getattr(item, "type", "") or "")


def _item_id(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("id") or item.get("rating_key") or "")
    return str(getattr(item, "id", "") or "")


def _fetch_text(url: str) -> str:
    # S310: URLs are module constants (Wikipedia/TMDB), never caller-supplied.
    req = urllib.request.Request(url, headers={"User-Agent": "plex-mcp/canon-coverage"})  # noqa: S310
    with urllib.request.urlopen(req, timeout=NETWORK_TIMEOUT) as resp:  # noqa: S310
        return resp.read().decode("utf-8", errors="replace")


def _cell_text(cell_html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", cell_html)).strip()


def _fetch_afi_100() -> list[dict[str, Any]]:
    """Parse the single AFI 2007-rank table. Raises on layout change."""
    html = _fetch_text(AFI_URL)
    tables = re.findall(r"<table[^>]*wikitable[^>]*>(.*?)</table>", html, re.S)
    if not tables:
        raise ValueError("No wikitable found on the AFI page (layout changed?)")
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", tables[0], re.S)
    films: list[dict[str, Any]] = []
    for r in rows[1:]:
        c = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)
        if len(c) < 6:
            continue
        title, year, rank = _cell_text(c[0]), _cell_text(c[1]), _cell_text(c[5])
        if title and re.fullmatch(r"\d{4}", year) and re.fullmatch(r"\d{1,3}", rank):
            films.append({"rank": int(rank), "title": title, "year": int(year)})
    if len(films) < 90:
        raise ValueError(f"AFI parse yielded only {len(films)} films (layout changed?)")
    films.sort(key=lambda f: f["rank"])
    return films


def _fetch_oscar_winners() -> list[dict[str, Any]]:
    """Parse decade tables: bold film cell == winner, year tracked via rowspans."""
    html = _fetch_text(OSCARS_URL)
    tables = re.findall(r"<table[^>]*wikitable[^>]*>(.*?)</table>", html, re.S)
    seen: dict[tuple[int, str], dict[str, Any]] = {}
    for t in tables:
        rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S)
        if not rows:
            continue
        hdr = [_cell_text(c).lower() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", rows[0], re.S)]
        if "film" not in hdr or "winner" in hdr:
            continue
        film_i = hdr.index("film")
        cur_year: int | None = None
        for r in rows[1:]:
            c = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)
            if not c:
                continue
            m = re.search(r"(\d{4})", _cell_text(c[0]))
            if m:
                cur_year = int(m.group(1))
            if len(c) > film_i and re.search(r"<b[\s>]", c[film_i]):
                title = _cell_text(c[film_i])
                if title and cur_year and (cur_year, title) not in seen:
                    seen[(cur_year, title)] = {"year": cur_year, "title": title}
    winners = sorted(seen.values(), key=lambda w: w["year"])
    if len(winners) < 90:
        raise ValueError(f"Oscar parse yielded only {len(winners)} winners (layout changed?)")
    return winners


def _tmdb_key() -> str:
    return os.environ.get("TMDB_API_KEY", "")


async def _fetch_tmdb_top(media: str, limit: int) -> list[dict[str, Any]]:
    """Live TMDB top_rated for movies and/or TV. Requires TMDB_API_KEY."""
    import httpx

    key = _tmdb_key()
    if not key:
        raise RuntimeError(
            "TMDB_API_KEY is not set. Set it in webapp/backend/.env (or Settings → LLM/TMDB) "
            "for TMDB canons, or use oscar_best_picture / afi_100 / check_list instead."
        )
    kinds = ["movie", "tv"] if media == "both" else [media]
    out: list[dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=20) as client:
        for kind in kinds:
            page = 1
            while len([e for e in out if e["kind"] == kind]) < limit:
                resp = await client.get(f"{TMDB_BASE}/{kind}/top_rated", params={"api_key": key, "page": page})
                if resp.status_code != 200:
                    raise RuntimeError(f"TMDB top_rated/{kind} returned HTTP {resp.status_code}.")
                results = resp.json().get("results") or []
                if not results:
                    break
                for r in results:
                    title = r.get("title") or r.get("name") or ""
                    date = r.get("release_date") or r.get("first_air_date") or ""
                    year = int(date[:4]) if date[:4].isdigit() else None
                    out.append(
                        {
                            "title": title,
                            "year": year,
                            "kind": kind,
                            "tmdb_rating": r.get("vote_average"),
                            "media_type": "movie" if kind == "movie" else "show",
                        }
                    )
                page += 1
                if page > 5:
                    break
    return out


async def _check_holdings(
    plex, entries: list[dict[str, Any]], want_type: str | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split canon entries into owned/missing via Plex search + title/year match."""
    owned: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for e in entries:
        title = e.get("title", "")
        try:
            results = await plex.search_media(query=title, limit=5)
        except Exception as ex:
            logger.warning("Holdings search failed for %r: %s", title, ex)
            missing.append({**e, "reason": "search failed"})
            continue
        hit = None
        for item in results or []:
            if want_type and _item_type(item) != want_type:
                continue
            if not _titles_match(title, _item_title(item)):
                continue
            if not _year_ok(e.get("year"), _item_year(item)):
                continue
            hit = {"id": _item_id(item), "title": _item_title(item), "year": _item_year(item)}
            break
        if hit:
            owned.append({**e, "held_as": hit})
        else:
            missing.append(e)
    return owned, missing


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def plex_canon(
    operation: Annotated[
        Literal["list_canons", "oscar_best_picture", "afi_100", "tmdb_top", "check_list"],
        Field(description="The canon operation to perform."),
    ],
    media_type: Annotated[
        Literal["movie", "show", "both"] | None,
        Field(description="tmdb_top scope (movies, TV, or both). Movie canons are movies-only."),
    ] = None,
    items: Annotated[
        list[dict[str, Any]] | None,
        Field(description="check_list entries: [{title, year?}] (max 200). Your 1001-style list goes here."),
    ] = None,
    limit: Annotated[int, Field(description="Max canon entries to check (latency cap).")] = 25,
) -> ToolResult:
    """
    Holdings-vs-canon gap analysis for builders.

    PORTMANTEAU PATTERN RATIONALE:
    Consolidates canon enumeration, live-list coverage (Oscars, AFI, TMDB),
    and caller-supplied lists (books, article series, website rankings like
    the 1001-Movies concept) into one matching engine.

    OPERATIONS:
    - list_canons: enumerate canons with sources and requirements (no network).
    - oscar_best_picture: every Best Picture winner vs your movie libraries.
    - afi_100: AFI 2007 top-100 vs your movie libraries.
    - tmdb_top: TMDB top-rated movies and/or TV (needs TMDB_API_KEY).
    - check_list: your own [{title, year?}] canon (book appendix, article
      series, website ranking) vs your libraries.

    ## Return Format
    {"success": bool, "operation": str, "data": {owned, missing, ...}, "message": str}

    ## Examples
    await plex_canon(operation="list_canons")
    await plex_canon(operation="afi_100", limit=25)
    await plex_canon(operation="check_list", items=[{"title": "Stalker", "year": 1979}])
    await plex_canon(operation="tmdb_top", media_type="show", limit=20)
    """
    try:
        if operation == "list_canons":
            return _ok(
                operation,
                {
                    "canons": [
                        {
                            "id": "oscar_best_picture",
                            "title": "Academy Award winners, Best Picture",
                            "source": OSCARS_URL,
                            "kind": "live Wikipedia table",
                            "media": "movie",
                            "requires": "network",
                        },
                        {
                            "id": "afi_100",
                            "title": "AFI 100 Years...100 Movies (2007)",
                            "source": AFI_URL,
                            "kind": "live Wikipedia table",
                            "media": "movie",
                            "requires": "network",
                        },
                        {
                            "id": "tmdb_top",
                            "title": "TMDB top-rated movies / TV",
                            "source": "https://api.themoviedb.org/3",
                            "kind": "live API",
                            "media": "movie, show, both",
                            "requires": "TMDB_API_KEY",
                        },
                        {
                            "id": "check_list",
                            "title": "Your list (1001-style book, article series, site ranking)",
                            "source": "caller-supplied items [{title, year?}]",
                            "kind": "matching only, no fetch",
                            "media": "movie (default; per item via media_type: movie|show)",
                            "requires": "items parameter",
                        },
                    ]
                },
                "4 canons available: 2 live movie lists, TMDB top (keyed), and your own list.",
            )

        plex = _get_plex_service()

        if operation == "oscar_best_picture":
            entries = _fetch_oscar_winners()[:limit]
            owned, missing = await _check_holdings(plex, entries, "movie")
            return _ok(
                operation,
                {
                    "canon": "oscar_best_picture",
                    "checked": len(entries),
                    "owned_count": len(owned),
                    "missing_count": len(missing),
                    "owned": owned,
                    "missing": missing,
                },
                f"Oscar winners: {len(owned)}/{len(entries)} held, {len(missing)} missing.",
            )

        if operation == "afi_100":
            entries = _fetch_afi_100()[:limit]
            owned, missing = await _check_holdings(plex, entries, "movie")
            return _ok(
                operation,
                {
                    "canon": "afi_100",
                    "checked": len(entries),
                    "owned_count": len(owned),
                    "missing_count": len(missing),
                    "owned": owned,
                    "missing": missing,
                },
                f"AFI 100: {len(owned)}/{len(entries)} held, {len(missing)} missing.",
            )

        if operation == "tmdb_top":
            media = media_type or "both"
            entries = (await _fetch_tmdb_top(media, limit))[:limit]
            movie_entries = [e for e in entries if e["media_type"] == "movie"]
            show_entries = [e for e in entries if e["media_type"] == "show"]
            owned_m, missing_m = await _check_holdings(plex, movie_entries, "movie")
            owned_s, missing_s = await _check_holdings(plex, show_entries, "show")
            return _ok(
                operation,
                {
                    "canon": "tmdb_top",
                    "media": media,
                    "checked": len(entries),
                    "owned_count": len(owned_m) + len(owned_s),
                    "missing_count": len(missing_m) + len(missing_s),
                    "owned": owned_m + owned_s,
                    "missing": missing_m + missing_s,
                },
                f"TMDB top ({media}): {len(owned_m) + len(owned_s)}/{len(entries)} held.",
            )

        if operation == "check_list":
            if not items:
                return _err(
                    operation,
                    "items is required for check_list.",
                    "MISSING_PARAMETER",
                    ["Pass [{title, year?}], e.g. a 1001-Movies slice"],
                )
            entries = [
                {"title": str(i.get("title", "")), "year": i.get("year"), "want_type": i.get("media_type", "movie")}
                for i in items[:_MAX_CHECK_ITEMS]
                if i.get("title")
            ]
            if not entries:
                return _err(operation, "No usable {title} entries in items.", "INVALID_PARAMETER", [])
            movie_entries = [
                {k: v for k, v in e.items() if k != "want_type"} for e in entries if e["want_type"] != "show"
            ]
            show_entries = [
                {k: v for k, v in e.items() if k != "want_type"} for e in entries if e["want_type"] == "show"
            ]
            owned_m, missing_m = await _check_holdings(plex, movie_entries, "movie")
            owned_s, missing_s = await _check_holdings(plex, show_entries, "show")
            return _ok(
                operation,
                {
                    "canon": "check_list",
                    "checked": len(entries),
                    "owned_count": len(owned_m) + len(owned_s),
                    "missing_count": len(missing_m) + len(missing_s),
                    "owned": owned_m + owned_s,
                    "missing": missing_m + missing_s,
                },
                f"Your list: {len(owned_m) + len(owned_s)}/{len(entries)} held.",
            )

        return _err(
            operation,
            f"Unknown operation: {operation}.",
            "INVALID_OPERATION",
            ["Use list_canons, oscar_best_picture, afi_100, tmdb_top, or check_list"],
        )
    except Exception as e:
        logger.error("Error in plex_canon operation '%s': %s", operation, e, exc_info=True)
        return _err(operation, str(e), "EXECUTION_ERROR")
