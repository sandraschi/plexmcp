"""Dashboard aggregation: one call for the Overview hero + KPI cards.

Combines server status, library inventory, enrichment/RAG/taste progress,
*arr reachability, and LLM provider state. Every source is best-effort:
a failure in one section yields null + an entry in `warnings`, never a 500.
"""

from __future__ import annotations

import logging
import os
import time

from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter()

_SERVER_START = time.time()


@router.get("/")
async def get_dashboard() -> dict:
    """Aggregate hero + KPI data for the Overview page."""
    warnings: list[str] = []
    payload: dict = {
        "success": True,
        "warnings": warnings,
    }

    # --- Plex server status -------------------------------------------------
    server_status: dict | None = None
    try:
        from ..mcp.client import mcp_client

        server_status = await mcp_client.call_tool("plex_server", {"operation": "status"})
    except Exception as e:
        warnings.append(f"server status unavailable: {e}")
        server_status = None
    payload["server"] = server_status

    # --- Libraries ----------------------------------------------------------
    libraries: list = []
    library_types: dict[str, int] = {}
    try:
        from ..mcp.client import mcp_client as _mc

        libs_result = await _mc.call_tool("plex_library", {"operation": "list"})
        data = libs_result.get("data") if isinstance(libs_result, dict) else None
        if isinstance(data, list):
            libraries = data
        for lib in libraries:
            if isinstance(lib, dict):
                t = str(lib.get("type") or "unknown")
                library_types[t] = library_types.get(t, 0) + 1
    except Exception as e:
        warnings.append(f"libraries unavailable: {e}")
    payload["libraries"] = {
        "count": len(libraries),
        "types": library_types,
        "items": [
            {
                "id": str(lib.get("id") or lib.get("key") or ""),
                "title": str(lib.get("title") or lib.get("name") or "Library"),
                "type": str(lib.get("type") or "unknown"),
            }
            for lib in libraries
            if isinstance(lib, dict)
        ][:25],
    }

    # --- Enrichment ---------------------------------------------------------
    try:
        from plex_mcp.services.enrichment.orchestrator import count_enriched

        payload["enrichment"] = {"enriched_count": count_enriched()}
    except Exception as e:
        warnings.append(f"enrichment stats unavailable: {e}")
        payload["enrichment"] = {"enriched_count": None}

    # --- RAG ----------------------------------------------------------------
    try:
        from ..mcp.client import mcp_client as _mc2

        rag_result = await _mc2.call_tool("plex_rag", {"operation": "status"})
        data = rag_result.get("data") if isinstance(rag_result.get("data"), dict) else {}
        payload["rag"] = {
            "available": bool(data.get("available")) if data else bool(rag_result.get("success")),
            "indexed_count": data.get("count") if data else None,
            "raw": rag_result,
        }
    except Exception as e:
        warnings.append(f"rag status unavailable: {e}")
        payload["rag"] = {"available": False, "indexed_count": None}

    try:
        from plex_mcp.services.rag_ingestor import get_rag_sync_progress

        payload["rag_sync"] = get_rag_sync_progress()
    except Exception:
        payload["rag_sync"] = {"phase": "unknown"}

    # --- Taste ----------------------------------------------------------------
    try:
        from plex_mcp.services.taste import sync as taste_sync

        st = taste_sync.status()
        payload["taste"] = {
            "built": bool(st.get("built")),
            "events": st.get("events"),
            "dimensions": st.get("dimensions"),
            "library_items": st.get("library_items"),
            "running": taste_sync.is_running(),
        }
    except Exception as e:
        warnings.append(f"taste status unavailable: {e}")
        payload["taste"] = {"built": False, "events": None}

    # --- *arr stack ------------------------------------------------------------
    try:
        from plex_mcp.services.arr_client import get_arr_stack_status

        payload["arr"] = await get_arr_stack_status()
    except Exception as e:
        warnings.append(f"arr status unavailable: {e}")
        payload["arr"] = {"success": False, "any_configured": False}

    # --- LLM providers ----------------------------------------------------------
    try:
        from .llm import get_providers as _get_providers

        providers = await _get_providers()
        payload["llm"] = providers
    except Exception as e:
        warnings.append(f"llm providers unavailable: {e}")
        payload["llm"] = {"providers": []}

    # --- Backend meta -------------------------------------------------------------
    payload["backend"] = {
        "uptime_seconds": int(time.time() - _SERVER_START),
        "plex_configured": bool(os.environ.get("PLEX_TOKEN")),
    }

    return payload
