"""File-based settings overrides. Applied to os.environ so MCP/LLM use them."""

import json
import os
from pathlib import Path

_KEYS = ("plex_token", "plex_url", "llm_provider", "llm_base_url", "llm_api_key")
_ENV_MAP = {
    "plex_token": "PLEX_TOKEN",
    "plex_url": "PLEX_URL",
    "llm_provider": "LLM_PROVIDER",
    "llm_base_url": "LLM_BASE_URL",
    "llm_api_key": "LLM_API_KEY",
}


def _path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "settings.json"


def load_and_apply() -> None:
    """Load data/settings.json and set os.environ. Call at startup after .env."""
    p = _path()
    if not p.exists():
        return
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return
    for key in _KEYS:
        if key in data and data[key] is not None and str(data[key]).strip():
            env_var = _ENV_MAP[key]
            if key == "plex_url":
                os.environ["PLEX_SERVER_URL"] = str(data[key]).strip()
            os.environ[env_var] = str(data[key]).strip()


def get_current() -> dict[str, str | bool | None]:
    """Return current effective values (from os.environ, then empty). Tokens masked."""
    out: dict[str, str | bool | None] = {}
    for key, env_var in _ENV_MAP.items():
        val = os.environ.get(env_var, "").strip()
        if "token" in key or "key" in key:
            out[key + "_set"] = bool(val)
            out[key] = "****" if val else None
        else:
            out[key] = val or None
    return out


def save_overrides(body: dict) -> None:
    """Write allowed keys to data/settings.json and update os.environ. Merges with existing file."""
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, str] = {}
    if p.exists():
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    for key in _KEYS:
        if key in body and body[key] is not None:
            s = str(body[key]).strip()
            data[key] = s
            env_var = _ENV_MAP[key]
            if key == "plex_url":
                os.environ["PLEX_SERVER_URL"] = s
            os.environ[env_var] = s
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
