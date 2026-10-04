"""Per-source fetchers for deep media enrichment.

Scope decision (2026-09-13): only sources with a real, documented API are called
here — Wikipedia (public REST API) and TMDB (official v3 API, deep mode). A third,
JustWatch, is included as a best-effort availability lookup against its public JSON
endpoint used by the wider community; it is treated as optional and never blocks
enrichment if unreachable. Letterboxd/IMDB/Rotten Tomatoes/Metacritic scraping was
explicitly excluded (their ToS prohibits scraping and they run active bot
detection) — see docs/plans/DEEP_METADATA_ENRICHMENT.md.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from ...utils import get_logger

logger = get_logger(__name__)

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
_TIMEOUT = 12.0
_UA = {"User-Agent": "plex-mcp/2.5 (+https://github.com/sandraschi/plexmcp)"}


async def fetch_wikipedia(title: str, year: int | None, media_type: str) -> dict[str, Any] | None:
    """Wikipedia REST summary (title/year, falling back to bare title)."""
    from ..enrichment_service import get_enrichment_service

    svc = get_enrichment_service()
    wiki = await svc.fetch_wikipedia_summary(title, year, media_type)
    return wiki


async def fetch_tmdb_deep(title: str, year: int | None, media_type: str, api_key: str) -> dict[str, Any] | None:
    """Full TMDB record: search -> details with credits/keywords/collection."""
    key = (api_key or os.environ.get("TMDB_API_KEY") or "").strip()
    if not key or not title.strip():
        return None

    is_tv = media_type in ("show", "series")
    search_path = "search/tv" if is_tv else "search/movie"
    params: dict[str, str] = {"api_key": key, "query": title.strip(), "include_adult": "false", "language": "en-US"}
    if year is not None:
        params["year" if not is_tv else "first_air_date_year"] = str(year)

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=_UA) as client:
            r = await client.get(f"https://api.themoviedb.org/3/{search_path}", params=params)
            if r.status_code != 200:
                logger.info("TMDB search %s -> %s", search_path, r.status_code)
                return None
            results = (r.json() or {}).get("results") or []
            if not results:
                return None
            tid = results[0].get("id")
            if tid is None:
                return None

            detail_path = f"tv/{tid}" if is_tv else f"movie/{tid}"
            append = "credits,keywords" + ("" if is_tv else ",release_dates,belongs_to_collection")
            dr = await client.get(
                f"https://api.themoviedb.org/3/{detail_path}",
                params={"api_key": key, "append_to_response": append, "language": "en-US"},
            )
            if dr.status_code != 200:
                return None
            detail = dr.json() or {}
    except Exception as e:
        logger.warning("TMDB deep fetch failed for %s: %s", title, e)
        return None

    credits_block = detail.get("credits") or {}
    crew = credits_block.get("crew") or []
    cast = credits_block.get("cast") or []
    director = next((c.get("name") for c in crew if c.get("job") == "Director"), None)
    writers = [c.get("name") for c in crew if c.get("job") in ("Writer", "Screenplay") and c.get("name")]
    keywords_block = detail.get("keywords") or {}
    keywords = [
        k.get("name") for k in (keywords_block.get("keywords") or keywords_block.get("results") or []) if k.get("name")
    ]
    collection = detail.get("belongs_to_collection")
    poster = detail.get("poster_path")

    return {
        "tmdb_id": tid,
        "title": detail.get("title") or detail.get("name") or title,
        "overview": detail.get("overview"),
        "genres": [g.get("name") for g in (detail.get("genres") or []) if g.get("name")],
        "runtime": detail.get("runtime") or (detail.get("episode_run_time") or [None])[0],
        "release_date": detail.get("release_date") or detail.get("first_air_date"),
        "vote_average": detail.get("vote_average"),
        "vote_count": detail.get("vote_count"),
        "budget": detail.get("budget"),
        "revenue": detail.get("revenue"),
        "production_companies": [c.get("name") for c in (detail.get("production_companies") or []) if c.get("name")],
        "countries": [c.get("name") for c in (detail.get("production_countries") or []) if c.get("name")],
        "poster_url": f"{TMDB_IMAGE_BASE}{poster}" if poster else None,
        "director": director,
        "writers": writers,
        "cast": [{"name": c.get("name"), "character": c.get("character")} for c in cast[:10] if c.get("name")],
        "keywords": keywords,
        "collection_id": collection.get("id") if isinstance(collection, dict) else None,
        "collection_name": collection.get("name") if isinstance(collection, dict) else None,
        "url": f"https://www.themoviedb.org/{'tv' if is_tv else 'movie'}/{tid}",
    }


async def fetch_justwatch(title: str, year: int | None, media_type: str) -> dict[str, Any] | None:
    """Best-effort streaming/availability lookup via JustWatch's public JSON API.

    Undocumented endpoint (no official API exists) — treated as low-signal and
    entirely optional. Any failure (schema change, rate limit, timeout) is
    swallowed and reported as an unavailable source, never a hard error.
    """
    try:
        content_type = "show" if media_type in ("show", "series") else "movie"
        body = {
            "query": title.strip(),
            "content_types": [content_type],
            "page_size": 3,
        }
        async with httpx.AsyncClient(timeout=8.0, headers=_UA) as client:
            r = await client.post(
                "https://apis.justwatch.com/content/titles/en_US/popular",
                json=body,
            )
            if r.status_code != 200:
                return None
            items = (r.json() or {}).get("items") or []
    except Exception as e:
        logger.info("JustWatch lookup skipped for %s: %s", title, e)
        return None

    if not items:
        return None

    match = items[0]
    if year is not None:
        for item in items:
            release_year = item.get("original_release_year")
            if release_year == year:
                match = item
                break

    offers = match.get("offers") or []
    providers = sorted({o.get("provider_id") for o in offers if o.get("provider_id")})
    monetization_types = sorted({o.get("monetization_type") for o in offers if o.get("monetization_type")})

    return {
        "jw_id": match.get("id"),
        "title": match.get("title"),
        "provider_ids": providers,
        "monetization_types": monetization_types,
        "offer_count": len(offers),
    }
