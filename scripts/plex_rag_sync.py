"""Plex metadata RAG sync — use with just rag-gpu-sync (venv python, not uv run)."""

from __future__ import annotations

import asyncio
import sys


async def _run(enrich: bool) -> int:
    from plex_mcp.rag.fastembed_gpu import embed_use_gpu, repo_root_from_here
    from plex_mcp.services.rag_ingestor import PlexIngestor
    from plex_mcp.tools.portmanteau.search import _get_plex_service

    gpu = embed_use_gpu(repo_root_from_here())
    print(f"[rag] GPU mode: {gpu}")

    plex = _get_plex_service()
    ingestor = PlexIngestor(plex)
    if not ingestor.is_available:
        print("[rag] RAG dependencies not available.", file=sys.stderr)
        return 1

    count = await ingestor.extract_and_index_all(enrich=enrich)
    print(f"[rag] Indexed {count} media items.")
    return 0 if count >= 0 else 1


def main() -> int:
    enrich = "--enrich" in sys.argv
    return asyncio.run(_run(enrich=enrich))


if __name__ == "__main__":
    raise SystemExit(main())
