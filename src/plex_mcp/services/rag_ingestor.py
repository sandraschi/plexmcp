import asyncio
import logging
import os
import sys
import threading
from typing import Any

from .enrichment_service import get_enrichment_service

logger = logging.getLogger(__name__)

_progress_lock = threading.Lock()
_sync_progress: dict[str, Any] = {"phase": "idle", "message": ""}


def get_rag_sync_progress() -> dict[str, Any]:
    """Snapshot of RAG reindex progress for webapp polling (thread-safe)."""
    with _progress_lock:
        return dict(_sync_progress)


def reset_rag_sync_progress() -> None:
    with _progress_lock:
        _sync_progress.clear()
        _sync_progress.update(
            {
                "phase": "idle",
                "message": "",
                "libraries_total": 0,
                "library_index": 0,
                "library_name": "",
                "documents_so_far": 0,
                "documents_total": 0,
            }
        )


def _report_progress(update: dict[str, Any]) -> None:
    with _progress_lock:
        _sync_progress.update(update)


def report_rag_sync_error(message: str) -> None:
    """Mark sync as failed (e.g. tool error before ingestor runs)."""
    _report_progress({"phase": "error", "message": message, "indexed_count": 0})


# 1) Try mcp-central-docs shared RAG (sibling repo)
_BaseVectorStore = None
HAS_RAG = False
_rag_backend = "none"

central_docs_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../mcp-central-docs/src"))
if os.path.exists(central_docs_src) and central_docs_src not in sys.path:
    sys.path.append(central_docs_src)
try:
    from docs_mcp.backend.rag_core import BaseVectorStore as _BaseVectorStore

    HAS_RAG = True
    _rag_backend = "mcp-central-docs"
except ImportError:
    pass

# 2) Fallback: in-repo LanceDB + fastembed (pip install fastembed lancedb)
if not HAS_RAG:
    try:
        import lancedb

        from plex_mcp.rag.fastembed_gpu import (
            EMBED_DIM,
            EMBED_MODEL,
            create_text_embedding,
            repo_root_from_here,
        )

        _embed_model_instance = None
        _embed_batch_size = 64

        def get_embed_model():
            """Lazy loader for FastEmbed (GPU when RAG_GPU=1 or .venv/rag-gpu-mode)."""
            global _embed_model_instance, _embed_batch_size
            if _embed_model_instance is None:
                cache = str(repo_root_from_here() / "data" / "embed_cache")
                _embed_model_instance, device, _embed_batch_size = create_text_embedding(
                    EMBED_MODEL, cache, repo_root=repo_root_from_here()
                )
                logger.info("FastEmbed device: %s (batch %s)", device, _embed_batch_size)
            return _embed_model_instance

        class LocalVectorStore:
            """In-repo RAG using LanceDB + fastembed. No mcp-central-docs needed."""

            def __init__(self, db_path: str, table_name: str = "plex_media", **kwargs):
                self.db_path = db_path
                self.table_name = table_name
                self.db = lancedb.connect(db_path)
                self._table = None

            def _ensure_table(self, dim: int = EMBED_DIM):
                if self._table is not None:
                    return
                try:
                    self._table = self.db.open_table(self.table_name)
                except Exception:
                    # Initialize with schema
                    if self.table_name == "plex_subtitles":
                        data = [
                            {
                                "id": "",
                                "content": "",
                                "vector": [0.0] * dim,
                                "metadata": {"media_id": "", "start_time": 0, "end_time": 0, "language": ""},
                            }
                        ]
                    else:
                        data = [{"id": "", "content": "", "vector": [0.0] * dim, "metadata": {}}]

                    self._table = self.db.create_table(
                        self.table_name,
                        data=data,
                        mode="overwrite",
                    )

            def add_documents(self, documents: list, overwrite: bool = True):
                if not documents:
                    return
                texts = [d.get("content", "") or "" for d in documents]
                model = get_embed_model()
                batch = _embed_batch_size
                all_vectors: list[list[float]] = []
                for start in range(0, len(texts), batch):
                    chunk = texts[start : start + batch]
                    for emb in model.embed(chunk):
                        vec = emb.tolist() if hasattr(emb, "tolist") else list(emb)
                        all_vectors.append(vec)
                rows = []
                for d, vec in zip(documents, all_vectors, strict=False):
                    rows.append(
                        {
                            "id": str(d.get("id", "")),
                            "content": d.get("content", ""),
                            "vector": vec,
                            "metadata": d.get("metadata") or {},
                        }
                    )
                self.db = lancedb.connect(self.db_path)
                if overwrite and self.table_name in self.db.table_names():
                    self.db.drop_table(self.table_name)
                self._table = self.db.create_table(self.table_name, data=rows, mode="overwrite")
                logger.info("Indexed %d documents into local LanceDB table %s", len(rows), self.table_name)

            def search(self, query: str, limit: int = 5, where: Any = None) -> list:
                try:
                    self.db = lancedb.connect(self.db_path)
                    self._table = self.db.open_table(self.table_name)
                except Exception:
                    return []
                qemb = list(get_embed_model().embed([query]))[0]
                qvec = qemb.tolist() if hasattr(qemb, "tolist") else list(qemb)
                results = self._table.search(qvec).limit(limit).to_list()
                out = []
                for r in results:
                    out.append(
                        {
                            "content": r.get("content", ""),
                            "metadata": r.get("metadata") or {},
                            "score": 1 - (r.get("_distance", 0) or 0),
                        }
                    )
                return out

            def count_rows(self) -> int:
                try:
                    self.db = lancedb.connect(self.db_path)
                    table = self.db.open_table(self.table_name)
                    return table.count_rows()
                except Exception:
                    return 0

        _BaseVectorStore = LocalVectorStore
        HAS_RAG = True
        _rag_backend = "lancedb"
    except ImportError:
        pass

if not HAS_RAG:

    class BaseVectorStore:
        def __init__(self, *args, **kwargs):
            pass

        def add_documents(self, documents, overwrite=True):
            pass

        def search(self, query, limit=5, where=None):
            return []

else:
    BaseVectorStore = _BaseVectorStore


class PlexIngestor:
    """Extracts and indexes Plex metadata into LanceDB for semantic search."""

    def __init__(self, plex_service, db_path: str = None):
        self.plex = plex_service
        self.db_path = db_path or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/lancedb"))
        self.vector_store = BaseVectorStore(db_path=self.db_path, table_name="plex_media")
        self.subtitle_store = BaseVectorStore(db_path=self.db_path, table_name="plex_subtitles")
        self.is_available = HAS_RAG

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        if not self.is_available:
            return {"available": False, "count": 0, "backend": "none"}

        count = 0
        if hasattr(self.vector_store, "count_rows"):
            count = self.vector_store.count_rows()

        return {
            "available": True,
            "count": count,
            "backend": _rag_backend,
            "db_path": self.db_path,
        }

    async def extract_and_index_all(self, enrich: bool = False):
        """Extracts Title, Plot/Summary, Genres, Directors (movies/shows) and artist summaries (music) into LanceDB."""
        reset_rag_sync_progress()
        try:
            return await self._extract_and_index_all_impl(enrich=enrich)
        except Exception as e:
            logger.exception("RAG extract_and_index_all failed: %s", e)
            _report_progress({"phase": "error", "message": str(e), "indexed_count": 0})
            return 0

    async def _extract_and_index_all_impl(self, enrich: bool = False) -> int:
        """Inner implementation after reset (see extract_and_index_all)."""
        if not self.is_available:
            logger.error("RAG Core is not available.")
            _report_progress(
                {
                    "phase": "error",
                    "message": "RAG dependencies not available. Install RAG extras or configure PYTHONPATH.",
                }
            )
            return 0

        _report_progress({"phase": "starting", "message": "Fetching libraries from Plex..."})

        libraries = await self.plex.get_libraries()
        eligible = [lib for lib in libraries if lib.get("type") in ("movie", "show", "artist")]
        total_libs = len(eligible)
        _report_progress(
            {
                "phase": "scanning",
                "libraries_total": total_libs,
                "library_index": 0,
                "message": f"Found {total_libs} eligible librar{'y' if total_libs == 1 else 'ies'} (movies, shows, music).",
            }
        )

        docs = []
        enrich_svc = get_enrichment_service() if enrich else None
        semaphore = asyncio.Semaphore(5)  # Limit concurrent enrichment requests

        for lib_idx, lib in enumerate(eligible):
            lib_id = str(lib.get("id"))
            lib_name = lib.get("title", "Unknown Library")
            lib_type = str(lib.get("type", ""))

            _report_progress(
                {
                    "phase": "processing_library",
                    "libraries_total": total_libs,
                    "library_index": lib_idx + 1,
                    "library_name": lib_name,
                    "library_type": lib_type,
                    "documents_so_far": len(docs),
                    "message": f'Reading "{lib_name}" ({lib_idx + 1}/{total_libs})...',
                }
            )

            try:
                # 1) Fetch main library items (Movies, Shows, Artist list)
                result = await self.plex.get_library_items(library_id=lib_id, limit=50000)
                items = result.get("items", [])

                # 2) If Show/Artist, also deep scan for Episodes/Albums
                if lib_type == "show":
                    _report_progress({"message": f'Reading episodes for "{lib_name}"...'})
                    ep_result = await self.plex.get_library_items(library_id=lib_id, libtype="episode", limit=50000)
                    items.extend(ep_result.get("items", []))
                elif lib_type == "artist":
                    _report_progress({"message": f'Reading albums for "{lib_name}"...'})
                    album_result = await self.plex.get_library_items(library_id=lib_id, libtype="album", limit=50000)
                    items.extend(album_result.get("items", []))

                for item in items:
                    key = str(item.get("id", item.get("key", "")))
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    year = item.get("year", "")
                    item_type = item.get("type", "unknown")

                    # Structure content with parent context
                    content = ""
                    parent = item.get("parent_title")
                    grandparent = item.get("grandparent_title")
                    idx = item.get("index")  # Episode/Album number
                    p_idx = item.get("parent_index")  # Season number

                    if item_type == "episode":
                        content = f"Show: {grandparent}\n"
                        if p_idx is not None and idx is not None:
                            content += f"Season {p_idx}, Episode {idx}: {title}\n"
                        else:
                            content += f"Episode: {title}\n"
                    elif item_type == "album":
                        content = f"Artist: {parent}\n"
                        content += f"Album: {title}\n"
                    else:
                        content = f"Title: {title}\n"

                    if year:
                        content += f"Year: {year}\n"

                    genres = list(item.get("genres", [])) if isinstance(item.get("genres"), list) else []
                    directors = list(item.get("directors", [])) if isinstance(item.get("directors"), list) else []

                    if genres:
                        content += f"Genres: {', '.join(genres)}\n"
                    if directors:
                        content += f"Directors: {', '.join(directors)}\n"
                    if summary:
                        content += f"Plot: {summary}\n"

                    content = content.strip()
                    if not content:
                        continue

                    safe_year = int(year) if str(year).isdigit() else 0

                    # High-Value Enrichment Callout
                    if enrich and enrich_svc:
                        async with semaphore:
                            # Use parent/grandparent for better enrichment matching if needed
                            match_title = title
                            if item_type == "episode" and grandparent:
                                match_title = f"{grandparent} {title}"
                            elif item_type == "album" and parent:
                                match_title = f"{parent} {title}"

                            enrichment = await enrich_svc.enrich_media(match_title, safe_year, item_type)
                            if enrichment and enrichment.get("wikipedia"):
                                wiki = enrichment["wikipedia"]
                                content += f"\n\nSource: Wikipedia ({wiki.get('url')})\n"
                                content += f"Context: {wiki.get('summary')}\n"
                                if wiki.get("description"):
                                    content += f"Era/Historical Context: {wiki.get('description')}\n"

                    doc = {
                        "id": key,
                        "content": content,
                        "metadata": {
                            "title": title,
                            "type": item_type,
                            "library": lib_name,
                            "year": safe_year,
                            "parent": parent or "",
                            "grandparent": grandparent or "",
                        },
                    }
                    docs.append(doc)
            except Exception as e:
                logger.exception("Error extracting items from library %s: %s", lib_name, e)

        if docs:
            _report_progress(
                {
                    "phase": "embedding",
                    "documents_total": len(docs),
                    "documents_so_far": len(docs),
                    "message": f"Embedding {len(docs)} document(s) and writing index (this can take a while)...",
                }
            )
            # Run blocking encode + LanceDB write in a thread so the event loop can serve /sync/status polls.
            await asyncio.to_thread(self.vector_store.add_documents, docs, True)
            _report_progress(
                {
                    "phase": "complete",
                    "indexed_count": len(docs),
                    "documents_total": len(docs),
                    "message": f"Indexed {len(docs)} item(s).",
                }
            )
            return len(docs)

        _report_progress(
            {
                "phase": "complete",
                "indexed_count": 0,
                "documents_total": 0,
                "message": "No documents to index (no eligible metadata).",
            }
        )
        return 0

    async def sync_subtitles(self, library_id: str | None = None, media_id: str | None = None) -> int:
        """Sync subtitles for a library or a specific media item."""
        if not self.is_available:
            return 0

        reset_rag_sync_progress()
        _report_progress({"phase": "starting", "message": "Analyzing subtitle tracks..."})

        try:
            items_to_process = []
            if media_id:
                item = await self.plex.get_media_info(media_id)
                if item:
                    items_to_process = [item]
            elif library_id:
                result = await self.plex.get_library_items(library_id=library_id, limit=50000)
                items_to_process = result.get("items", [])
            else:
                libraries = await self.plex.get_libraries()
                for lib in libraries:
                    if lib.get("type") in ("movie", "show"):
                        result = await self.plex.get_library_items(library_id=str(lib["id"]), limit=50000)
                        items_to_process.extend(result.get("items", []))

            total_items = len(items_to_process)
            _report_progress(
                {
                    "phase": "extracting",
                    "documents_total": total_items,
                    "message": f"Found {total_items} items to check for subtitles.",
                }
            )

            all_chunks = []
            for idx, item in enumerate(items_to_process):
                rating_key = str(item.get("id"))
                title = item.get("title", "Unknown")

                _report_progress(
                    {
                        "library_index": idx + 1,
                        "library_name": title,
                        "message": f"Processing subtitles for: {title} ({idx + 1}/{total_items})",
                    }
                )

                chunks = await self._extract_subtitles_for_item(rating_key, title)
                all_chunks.extend(chunks)

            if all_chunks:
                _report_progress({"phase": "embedding", "message": f"Embedding {len(all_chunks)} subtitle chunks..."})
                await asyncio.to_thread(self.subtitle_store.add_documents, all_chunks, True)
                _report_progress(
                    {
                        "phase": "complete",
                        "message": f"Successfully indexed {len(all_chunks)} subtitle chunks from {total_items} items.",
                    }
                )
                return len(all_chunks)

            _report_progress({"phase": "complete", "message": "No subtitles found to index."})
            return 0

        except Exception as e:
            logger.exception("Subtitle sync failed: %s", e)
            _report_progress({"phase": "error", "message": str(e)})
            return 0

    async def _extract_subtitles_for_item(self, media_id: str, title: str) -> list[dict[str, Any]]:
        """Download and parse subtitles for a specific media item."""
        try:
            # Use the server's fetchItem to get the full object with streams
            server_item = await asyncio.to_thread(self.plex.server.fetchItem, int(media_id))

            chunks = []
            for media in server_item.media:
                for part in media.parts:
                    for stream in part.streams:
                        # streamType 3 is Subtitle
                        if getattr(stream, "streamType", 0) == 3 and getattr(stream, "key", None):
                            codec = getattr(stream, "codec", "").lower()
                            if codec in ("srt", "vtt"):
                                content = await self._download_subtitle(stream.key)
                                if content:
                                    item_chunks = self._parse_and_chunk_subtitle(
                                        content, media_id, title, getattr(stream, "language", "en")
                                    )
                                    chunks.extend(item_chunks)
                                    # Break after first successful subtitle track to avoid duplicates
                                    return chunks
            return chunks
        except Exception as e:
            logger.exception(f"Error extracting subtitles for {title} ({media_id}): {e}")
            return []

    async def _download_subtitle(self, key: str) -> str | None:
        """Download subtitle content from Plex server."""
        import httpx

        url = self.plex.server.url(key)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            logger.exception(f"Failed to download subtitle from {url}: {e}")
        return None

    def _parse_srt(self, content: str) -> list[dict[str, Any]]:
        """Parse SRT content into a list of dialogue blocks."""
        # Pattern for: 00:00:20,000 --> 00:00:24,400
        pattern = r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})"
        return self._slice_subtitle_content(content, pattern, ",", ":")

    def _parse_vtt(self, content: str) -> list[dict[str, Any]]:
        """Parse VTT content into a list of dialogue blocks."""
        import re

        if content.startswith("WEBVTT"):
            content = re.sub(r"WEBVTT.*\n", "", content, count=1)
        # Pattern for: 00:00:20.000 --> 00:00:24.400
        pattern = r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})"
        return self._slice_subtitle_content(content, pattern, ".", ":")

    def _slice_subtitle_content(
        self, content: str, pattern: str, decimal_sep: str, time_sep: str
    ) -> list[dict[str, Any]]:
        import re

        blocks = re.split(pattern, content)
        results = []
        for i in range(1, len(blocks), 3):
            if i + 2 >= len(blocks):
                break
            start_ts = blocks[i].strip()
            end_ts = blocks[i + 1].strip()
            text = blocks[i + 2].strip()

            # Remove HTML tags and sequence numbers (including those at the end of blocks)
            text = re.sub(r"<[^>]*>", "", text)
            text = re.sub(r"^\d+\s*\n", "", text)  # Leading sequence number
            text = re.sub(r"\n\s*\d+\s*$", "", text)  # Trailing sequence number (from re.split overlap)
            text = " ".join(text.split())

            if not text:
                continue

            def to_ms(ts):
                ts = ts.replace(decimal_sep, ".")
                parts = re.split(f"[{time_sep}.]", ts)
                if len(parts) < 4:
                    return 0
                h, m, s, ms = map(int, parts)
                return (h * 3600 + m * 60 + s) * 1000 + ms

            results.append({"start_ms": to_ms(start_ts), "end_ms": to_ms(end_ts), "text": text})
        return results

    def _chunk_dialogue(self, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Group blocks into larger overlapping chunks."""
        chunk_size = 8
        overlap = 2
        chunks = []
        for i in range(0, len(blocks), chunk_size - overlap):
            group = blocks[i : i + chunk_size]
            if not group:
                break
            combined_text = " ".join([r["text"] for r in group])
            chunks.append({"start_ms": group[0]["start_ms"], "end_ms": group[-1]["end_ms"], "text": combined_text})
        return chunks

    def _parse_and_chunk_subtitle(self, content: str, media_id: str, title: str, lang: str) -> list[dict[str, Any]]:
        """Parse SRT/VTT and create chunks of dialogue."""
        if "-->" not in content:
            return []

        # Determine format
        if content.startswith("WEBVTT") or ".000 -->" in content:
            blocks = self._parse_vtt(content)
        else:
            blocks = self._parse_srt(content)

        chunks = self._chunk_dialogue(blocks)

        results = []
        for i, chunk in enumerate(chunks):
            start_time = chunk["start_ms"]
            end_time = chunk["end_ms"]

            def format_time(ms):
                s = ms // 1000
                return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

            results.append(
                {
                    "id": f"{media_id}_sub_{i}",
                    "content": f"Media: {title}\nTime: {format_time(start_time)} - {format_time(end_time)}\nDialogue: {chunk['text']}",
                    "metadata": {
                        "media_id": media_id,
                        "title": title,
                        "start_time": start_time,
                        "end_time": end_time,
                        "language": lang,
                    },
                }
            )
        return results

    def semantic_search(self, query: str, limit: int = 5, table: str = "plex_media"):
        if not self.is_available:
            return []
        store = self.vector_store if table == "plex_media" else self.subtitle_store
        return store.search(query, limit=limit)
