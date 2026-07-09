"""File-based settings overrides. Applied to os.environ so MCP/LLM use them."""

import json
import os
import sys
from pathlib import Path

_KEYS = (
    "plex_token",
    "plex_url",
    "llm_provider",
    "llm_base_url",
    "llm_api_key",
    "tmdb_api_key",
    "radarr_url",
    "radarr_api_key",
    "sonarr_url",
    "sonarr_api_key",
    "lidarr_url",
    "lidarr_api_key",
)
_ENV_MAP = {
    "plex_token": "PLEX_TOKEN",
    "plex_url": "PLEX_URL",
    "llm_provider": "LLM_PROVIDER",
    "llm_base_url": "LLM_BASE_URL",
    "llm_api_key": "LLM_API_KEY",
    "tmdb_api_key": "TMDB_API_KEY",
    "radarr_url": "RADARR_URL",
    "radarr_api_key": "RADARR_API_KEY",
    "sonarr_url": "SONARR_URL",
    "sonarr_api_key": "SONARR_API_KEY",
    "lidarr_url": "LIDARR_URL",
    "lidarr_api_key": "LIDARR_API_KEY",
}
# Uppercase .env keys → settings.json keys
_DOTENV_TO_SETTINGS = {
    "PLEX_TOKEN": "plex_token",
    "PLEX_URL": "plex_url",
    "LLM_PROVIDER": "llm_provider",
    "LLM_BASE_URL": "llm_base_url",
    "LLM_API_KEY": "llm_api_key",
    "TMDB_API_KEY": "tmdb_api_key",
    "RADARR_URL": "radarr_url",
    "RADARR_API_KEY": "radarr_api_key",
    "SONARR_URL": "sonarr_url",
    "SONARR_API_KEY": "sonarr_api_key",
    "LIDARR_URL": "lidarr_url",
    "LIDARR_API_KEY": "lidarr_api_key",
}


def _app_data_dir() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", ".")) / "ai.fleet.plex-mcp"


def _path() -> Path:
    if getattr(sys, "frozen", False) or os.environ.get("PLEX_TAURI") == "1":
        base = _app_data_dir()
    else:
        base = Path(__file__).resolve().parent.parent / "data"
    return base / "settings.json"


def _dotenv_path() -> Path:
    """Single .env location — repo root. One source of truth, no fallback chain."""
    backend_dir = Path(__file__).resolve().parent.parent
    return backend_dir.parent.parent / ".env"


def _parse_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value:
                out[key] = value
    except OSError:
        return {}
    return out


def _import_dotenv_into_settings() -> None:
    """Import .env into settings.json. .env ALWAYS wins over cached settings.json."""
    p = _path()
    data: dict[str, str] = {}
    if p.exists():
        try:
            with p.open(encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data = {k: str(v) for k, v in loaded.items() if v is not None}
        except (json.JSONDecodeError, OSError):
            pass

    merged = dict(data)
    env_path = _dotenv_path()
    if env_path.is_file():
        parsed = _parse_dotenv(env_path)
        for env_key, settings_key in _DOTENV_TO_SETTINGS.items():
            val = parsed.get(env_key, "").strip()
            if val:
                merged[settings_key] = val
    if merged != data:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)


def load_and_apply() -> None:
    """Load settings.json (importing .env first if needed) and set os.environ."""
    _import_dotenv_into_settings()
    p = _path()
    if not p.exists():
        return
    try:
        with p.open(encoding="utf-8") as f:
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
    """Write allowed keys to settings.json and update os.environ. Merges with existing file."""
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, str] = {}
    if p.exists():
        try:
            with p.open(encoding="utf-8") as f:
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
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
