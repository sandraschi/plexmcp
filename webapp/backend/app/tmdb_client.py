"""TMDB API v3 lookup for webapp AI context (optional API key)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w342"


async def tmdb_lookup_title(
    api_key: str,
    title: str,
    year: int | None,
    media_type: str,
) -> dict[str, Any] | None:
    """
    Return best-match movie or TV record: id, title, overview, poster_url, url, vote_average.
    """
    key = (api_key or "").strip()
    if not key or not (title or "").strip():
        return None

    is_tv = media_type == "show"
    path = "search/tv" if is_tv else "search/movie"
    params: dict[str, str] = {
        "api_key": key,
        "query": title.strip(),
        "include_adult": "false",
        "language": "en-US",
    }
    if year is not None:
        params["year" if not is_tv else "first_air_date_year"] = str(year)

    url = f"https://api.themoviedb.org/3/{path}"
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(url, params=params)
            if r.status_code != 200:
                logger.info("TMDB %s returned %s", path, r.status_code)
                return None
            data = r.json()
    except Exception as e:
        logger.warning("TMDB request failed: %s", e)
        return None

    results = data.get("results") or []
    if not isinstance(results, list) or not results:
        return None

    top = results[0]
    if not isinstance(top, dict):
        return None

    tid = top.get("id")
    if tid is None:
        return None

    name = (top.get("title") or top.get("name") or title or "").strip()
    overview = (top.get("overview") or "").strip() or None
    poster = top.get("poster_path")
    poster_url = f"{TMDB_IMAGE_BASE}{poster}" if poster else None
    vote = top.get("vote_average")
    slug = "tv" if is_tv else "movie"
    page_url = f"https://www.themoviedb.org/{slug}/{tid}"

    return {
        "id": int(tid),
        "title": name,
        "overview": overview,
        "poster_url": poster_url,
        "url": page_url,
        "vote_average": float(vote) if vote is not None else None,
        "release_date": top.get("release_date") or top.get("first_air_date"),
    }
