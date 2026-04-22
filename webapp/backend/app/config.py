"""Configuration for PlexMCP webapp backend."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env next to webapp/backend/ so it's found regardless of cwd
_env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=_env_path if _env_path.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    API_TITLE: str = "PlexMCP Webapp API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "HTTP API wrapper for PlexMCP server"

    HOST: str = "0.0.0.0"  # noqa: S104
    PORT: int = 10740
    RELOAD: bool = True

    CORS_ORIGINS: str = "http://localhost:10741,http://127.0.0.1:10741"

    @property
    def cors_origins_list(self) -> list[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

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
