"""Log file API for webapp logger modal."""

import os
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter()


def _log_path() -> Path | None:
    if os.environ.get("LOG_FILE"):
        p = Path(os.environ["LOG_FILE"])
        if p.is_absolute():
            return p if p.exists() else None
    root = Path(__file__).resolve().parent.parent.parent.parent.parent
    for name in ("webapp.log", "plex-mcp.log"):
        candidate = root / "logs" / name
        if candidate.exists():
            return candidate.resolve()
    return None


@router.get("")
async def get_logs(
    tail: int = Query(500, ge=1, le=10000, description="Last N lines"),
    filter_substring: str | None = Query(None, alias="filter", description="Substring filter"),
    level: str | None = Query(None, description="Log level filter (DEBUG,INFO,WARNING,ERROR)"),
):
    """Return tail of log file with optional filter. For logger modal."""
    log_path = _log_path()
    if not log_path:
        return {"lines": [], "total": 0, "error": "No log file found", "file": None}
    try:
        with open(log_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        return {"lines": [], "total": 0, "error": str(e), "file": str(log_path)}

    if filter_substring:
        fl = filter_substring.lower()
        lines = [ln for ln in lines if fl in ln.lower()]
    if level:
        lv = level.upper()
        lines = [ln for ln in lines if f'"{lv}"' in ln or f" - {lv} - " in ln]

    total = len(lines)
    lines = lines[-tail:] if tail < total else lines
    return {"lines": lines, "total": total, "file": str(log_path), "error": None}
