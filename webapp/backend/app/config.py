"""Configuration for PlexMCP webapp backend."""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_files() -> tuple[str, ...] | None:
    paths: list[Path] = []
    app_env = Path(os.environ.get("LOCALAPPDATA", "")) / "ai.fleet.plex-mcp" / ".env"
    if app_env.is_file():
        paths.append(app_env)
    backend_env = Path(__file__).resolve().parent.parent / ".env"
    if backend_env.is_file():
        paths.append(backend_env)
    repo_env = backend_env.parent.parent / ".env"
    if repo_env.is_file():
        paths.append(repo_env)
    return tuple(str(p) for p in paths) if paths else None


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    API_TITLE: str = "PlexMCP Webapp API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "HTTP API wrapper for PlexMCP server"

    HOST: str = "0.0.0.0"  # noqa: S104
    PORT: int = 10740
    RELOAD: bool = True

    CORS_ORIGINS: str = (
        "http://localhost:10741,http://127.0.0.1:10741,http://goliath:10741,http://goliath:10740,http://tauri.localhost,https://tauri.localhost,tauri://localhost"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]
        if os.environ.get("PLEX_TAURI", "").lower() in ("1", "true", "yes"):
            for extra in (
                "http://tauri.localhost",
                "https://tauri.localhost",
                "tauri://localhost",
            ):
                if extra not in origins:
                    origins.append(extra)
        return origins

    PLEX_URL: str = "http://localhost:32400"
    PLEX_TOKEN: str = ""

    # LLM (Ollama, LM Studio, OpenAI-compatible)
    LLM_PROVIDER: str = "ollama"
    LLM_BASE_URL: str = "http://127.0.0.1:11434"
    LLM_API_KEY: str = ""

    # Optional: TMDB v3 for AI context panel (poster, match URL, overview)
    TMDB_API_KEY: str = ""

    # Optional: light RAG over Plex metadata
    RAG_INDEX_ENABLED: bool = False
    RAG_EMBED_MODEL: str = "nomic-embed-text"


settings = Settings()
