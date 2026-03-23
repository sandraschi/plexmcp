"""Environment-driven config for PlexMCP sampling (FastMCP 3.1)."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _default_sampling_base_url() -> str:
    """Prefer PLEX_SAMPLING_BASE_URL; else derive from LLM_BASE_URL (webapp / Ollama)."""
    explicit = (os.getenv("PLEX_SAMPLING_BASE_URL") or "").strip()
    if explicit:
        return explicit.rstrip("/")
    llm = (os.getenv("LLM_BASE_URL") or "").strip().rstrip("/")
    if not llm:
        return "http://127.0.0.1:11434/v1"
    if llm.endswith("/v1"):
        return llm
    if ":11434" in llm or "ollama" in llm.lower():
        return llm + "/v1"
    return llm if "/v1" in llm else llm + "/v1"


@dataclass
class PlexSamplingConfig:
    """OpenAI-compatible chat/completions endpoint for MCP sampling."""

    sampling_base_url: str
    sampling_model: str
    sampling_api_key: str | None

    @classmethod
    def from_env(cls) -> PlexSamplingConfig:
        return cls(
            sampling_base_url=_default_sampling_base_url(),
            sampling_model=os.getenv("PLEX_SAMPLING_MODEL", os.getenv("LLM_MODEL", "llama3.2")),
            sampling_api_key=(os.getenv("PLEX_SAMPLING_API_KEY") or None),
        )
