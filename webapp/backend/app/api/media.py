"""Single-item Plex media metadata + lazy AI / external context (for webapp)."""

import logging
import os
from typing import Any
from urllib.parse import quote_plus

import httpx
from fastapi import APIRouter, HTTPException, Query

from ..config import settings
from ..mcp.client import mcp_client
from ..media_ai_context_cache import read_cached, write_cached
from ..tmdb_client import tmdb_lookup_title
from ..utils.errors import handle_mcp_error

logger = logging.getLogger(__name__)

router = APIRouter()


async def _try_llm_movie_notes(title: str, year: int | None, wiki_extract: str | None) -> str | None:
    """Optional short LLM layer on top of Wikipedia (Ollama or OpenAI-compatible)."""
    if not wiki_extract or len(wiki_extract.strip()) < 60:
        return None
    base = (os.environ.get("LLM_BASE_URL") or settings.LLM_BASE_URL or "").strip().rstrip("/")
    if not base:
        return None
    model = (os.environ.get("LLM_MODEL") or "gemma4:12b").strip()
    # override from query param when provided
    model = (query_params.get("llm_model") or model)
    clip = wiki_extract.strip()[:4000]
    user = (
        f"Plex library item: title={title!r}, year={year!r}.\n"
        "Below is a Wikipedia extract. Add 3–5 short bullet lines with extra context "
        "(production, reception, cultural/historical note) that add information and do not "
        "repeat the extract verbatim. If you are unsure, output fewer bullets. "
        "Plain lines starting with '- ', no title, no markdown headings.\n\n"
        f"Extract:\n{clip}"
    )
    messages = [{"role": "user", "content": user}]
    try:
        async with httpx.AsyncClient(timeout=50.0) as client:
            if ":11434" in base or "ollama" in base.lower():
                r = await client.post(
                    f"{base}/api/chat",
                    json={"model": model, "messages": messages, "stream": False},
                )
                if r.status_code != 200:
                    return None
                data = r.json()
                return ((data.get("message") or {}).get("content") or "").strip() or None
            headers = {"Content-Type": "application/json"}
            key = os.environ.get("LLM_API_KEY") or settings.LLM_API_KEY
            if key:
                headers["Authorization"] = f"Bearer {key}"
            r = await client.post(
                f"{base}/v1/chat/completions",
                headers=headers,
                json={"model": model, "messages": messages, "stream": False},
            )
            if r.status_code != 200:
                return None
            data = r.json()
            ch0 = (data.get("choices") or [{}])[0] or {}
            msg = (ch0.get("message") or {}).get("content") or ""
            return msg.strip() or None
    except Exception as e:
        logger.info("LLM enrichment skipped or failed: %s", e)
        return None


async def _build_media_ai_context_payload(rating_key: str) -> dict[str, Any]:
    """Compute Wikipedia, TMDB (when API key set), links, and optional LLM notes."""
    result = await mcp_client.call_tool(
        "plex_media",
        {"operation": "get_details", "media_key": rating_key},
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=404,
            detail=str(result.get("error") or "Media not found"),
        )
    data = result.get("data")
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=404, detail="No metadata returned")

    title = str(data.get("title") or data.get("name") or "").strip() or "Unknown"
    raw_year = data.get("year")
    year: int | None
    try:
        year = int(raw_year) if raw_year is not None and str(raw_year).strip() != "" else None
    except (TypeError, ValueError):
        year = None
    mtype = str(data.get("type") or "movie").lower()
    media_type = "show" if mtype in ("show", "series") else "movie"

    wiki_block: dict[str, Any] | None = None
    try:
        from plex_mcp.services.enrichment_service import get_enrichment_service

        svc = get_enrichment_service()
        enriched = await svc.enrich_media(title, year, media_type)
        w = enriched.get("wikipedia") if isinstance(enriched, dict) else None
        if isinstance(w, dict) and (w.get("summary") or "").strip():
            wiki_block = w
    except Exception as e:
        logger.warning("Wikipedia enrichment failed for %s: %s", rating_key, e)

    wiki_extract = (wiki_block or {}).get("summary") if wiki_block else None
    llm_notes = await _try_llm_movie_notes(title, year, wiki_extract if isinstance(wiki_extract, str) else None)

    tmdb_key = (os.environ.get("TMDB_API_KEY") or getattr(settings, "TMDB_API_KEY", "") or "").strip()
    tmdb_match: dict[str, Any] | None = None
    if tmdb_key:
        try:
            tmdb_match = await tmdb_lookup_title(tmdb_key, title, year, media_type)
        except Exception as e:
            logger.info("TMDB lookup skipped: %s", e)

    q = quote_plus(title)
    links: dict[str, str] = {
        "tmdb_search": f"https://www.themoviedb.org/search?query={q}",
        "wikipedia_search": f"https://en.wikipedia.org/w/index.php?search={q}",
    }
    if wiki_block and wiki_block.get("url"):
        links["wikipedia_article"] = wiki_block["url"]
    if tmdb_match and tmdb_match.get("url"):
        links["tmdb_match"] = tmdb_match["url"]

    return {
        "success": True,
        "rating_key": rating_key,
        "plex": {"title": title, "year": year, "type": media_type},
        "wikipedia": wiki_block,
        "tmdb": tmdb_match,
        "links": links,
        "llm_notes": llm_notes,
    }


@router.get("/{rating_key}/ai-context")
async def get_media_ai_context(
    rating_key: str,
    refresh: bool = Query(False, description="Bypass cache and rebuild context"),
) -> dict[str, Any]:
    """
    Resolve Plex item by rating key, then attach Wikipedia, TMDB (with API key),
    search links, and optional LLM bullet notes. Cached on disk (default 7 days).
    """
    try:
        if not refresh:
            hit = read_cached(rating_key)
            if hit:
                return {**hit, "cached": True}

        payload = await _build_media_ai_context_payload(rating_key)
        write_cached(rating_key, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return {**payload, "cached": False}


@router.get("/{rating_key}")
async def get_media_detail(rating_key: str) -> dict[str, Any]:
    """Return full formatted metadata for one library item (rating key)."""
    try:
        result = await mcp_client.call_tool(
            "plex_media",
            {"operation": "get_details", "media_key": rating_key},
        )
        if not result.get("success"):
            raise HTTPException(  # noqa: TRY301
                status_code=404,
                detail=str(result.get("error") or "Media not found"),
            )
        data = result.get("data")
        if not data:
            raise HTTPException(  # noqa: TRY301
                status_code=404,
                detail="No metadata returned",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_mcp_error(e) from e
    else:
        return {"success": True, "data": data}
