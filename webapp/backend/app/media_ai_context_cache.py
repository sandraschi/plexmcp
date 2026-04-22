"""File cache for GET /api/media/{rating_key}/ai-context responses."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _cache_dir() -> Path:
    p = Path(__file__).resolve().parent.parent / "data" / "media_ai_context"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _safe_filename(rating_key: str) -> str:
    s = re.sub(r"[^\w\-]", "_", (rating_key or "").strip())[:120]
    return s or "unknown"


def _ttl_seconds() -> float:
    try:
        return float(os.environ.get("MEDIA_AI_CONTEXT_CACHE_TTL_SEC", "604800"))
    except ValueError:
        return 604800.0


def read_cached(rating_key: str) -> dict[str, Any] | None:
    path = _cache_dir() / f"{_safe_filename(rating_key)}.json"
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        wrapper = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        logger.debug("Cache read miss %s: %s", path, e)
        return None

    if not isinstance(wrapper, dict):
        return None
    ts = wrapper.get("cached_at")
    payload = wrapper.get("payload")
    if not isinstance(payload, dict) or ts is None:
        return None
    try:
        age = time.time() - float(ts)
    except (TypeError, ValueError):
        return None
    if age > _ttl_seconds() or age < -60:
        return None
    return payload


def write_cached(rating_key: str, payload: dict[str, Any]) -> None:
    path = _cache_dir() / f"{_safe_filename(rating_key)}.json"
    wrapper = {"cached_at": time.time(), "payload": payload}
    try:
        path.write_text(json.dumps(wrapper, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        logger.warning("Could not write AI context cache %s: %s", path, e)
