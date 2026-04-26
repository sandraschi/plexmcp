"""
Optional *arr stack HTTP probes (Radarr, Sonarr, Lidarr).

Uses each app's REST API with X-Api-Key. Configure via environment:

- RADARR_URL, RADARR_API_KEY
- SONARR_URL, SONARR_API_KEY
- LIDARR_URL, LIDARR_API_KEY
"""

from __future__ import annotations

import os
from typing import Any

import httpx

_TIMEOUT = 10.0


async def _probe_v3(name: str, base: str, api_key: str) -> dict[str, Any]:
    """Radarr / Sonarr use API v3."""
    base = base.rstrip("/")
    headers = {"X-Api-Key": api_key}
    prefix = "/api/v3"
    async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
        try:
            r = await client.get(f"{base}{prefix}/system/status", headers=headers)
            r.raise_for_status()
            body = r.json()
            version = body.get("version", "?")
            qc: int | None = None
            try:
                qr = await client.get(f"{base}{prefix}/queue", headers=headers)
                if qr.status_code == 200:
                    qj = qr.json()
                    qc = int(qj.get("totalRecords", 0))
                    if qc == 0 and isinstance(qj.get("records"), list):
                        qc = len(qj["records"])
            except Exception:
                qc = None
            return {
                "name": name,
                "configured": True,
                "reachable": True,
                "version": str(version) if version is not None else None,
                "queue_count": qc,
                "error": None,
            }
        except Exception as e:
            return {
                "name": name,
                "configured": True,
                "reachable": False,
                "version": None,
                "queue_count": None,
                "error": str(e),
            }


async def _probe_v1(name: str, base: str, api_key: str) -> dict[str, Any]:
    """Lidarr uses API v1."""
    base = base.rstrip("/")
    headers = {"X-Api-Key": api_key}
    prefix = "/api/v1"
    async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
        try:
            r = await client.get(f"{base}{prefix}/system/status", headers=headers)
            r.raise_for_status()
            body = r.json()
            version = body.get("version")
            qc: int | None = None
            try:
                qr = await client.get(f"{base}{prefix}/queue", headers=headers)
                if qr.status_code == 200:
                    qj = qr.json()
                    qc = int(qj.get("totalRecords", 0))
                    if qc == 0 and isinstance(qj.get("records"), list):
                        qc = len(qj["records"])
            except Exception:
                qc = None
            return {
                "name": name,
                "configured": True,
                "reachable": True,
                "version": str(version) if version is not None else None,
                "queue_count": qc,
                "error": None,
            }
        except Exception as e:
            return {
                "name": name,
                "configured": True,
                "reachable": False,
                "version": None,
                "queue_count": None,
                "error": str(e),
            }


async def get_arr_stack_status() -> dict[str, Any]:
    """
    Return connectivity and queue snapshot for Radarr, Sonarr, Lidarr from environment.

    Reads RADARR_URL / RADARR_API_KEY, SONARR_*, LIDARR_* (same names as webapp settings).
    """
    radarr_u = os.environ.get("RADARR_URL", "").strip()
    radarr_k = os.environ.get("RADARR_API_KEY", "").strip()
    sonarr_u = os.environ.get("SONARR_URL", "").strip()
    sonarr_k = os.environ.get("SONARR_API_KEY", "").strip()
    lidarr_u = os.environ.get("LIDARR_URL", "").strip()
    lidarr_k = os.environ.get("LIDARR_API_KEY", "").strip()

    if radarr_u and radarr_k:
        radarr = await _probe_v3("radarr", radarr_u, radarr_k)
    else:
        radarr = {
            "name": "radarr",
            "configured": False,
            "reachable": False,
            "version": None,
            "queue_count": None,
            "error": None,
        }

    if sonarr_u and sonarr_k:
        sonarr = await _probe_v3("sonarr", sonarr_u, sonarr_k)
    else:
        sonarr = {
            "name": "sonarr",
            "configured": False,
            "reachable": False,
            "version": None,
            "queue_count": None,
            "error": None,
        }

    if lidarr_u and lidarr_k:
        lidarr = await _probe_v1("lidarr", lidarr_u, lidarr_k)
    else:
        lidarr = {
            "name": "lidarr",
            "configured": False,
            "reachable": False,
            "version": None,
            "queue_count": None,
            "error": None,
        }

    any_configured = any(x.get("configured") for x in (radarr, sonarr, lidarr) if isinstance(x, dict))
    return {
        "success": True,
        "any_configured": any_configured,
        "radarr": radarr,
        "sonarr": sonarr,
        "lidarr": lidarr,
        "hint": "Set RADARR_*/SONARR_*/LIDARR_* URL and API keys (webapp Settings or .env). URLs must match your Docker/media stack (host:port or reverse proxy).",
    }
