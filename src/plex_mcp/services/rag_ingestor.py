import asyncio
import logging
import os
import sys
import threading
from typing import Any

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

central_docs_src = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../mcp-central-docs/src")
)
if os.path.exists(central_docs_src) and central_docs_src not in sys.path:
    sys.path.append(central_docs_src)
try:
    from docs_mcp.backend.rag_core import BaseVectorStore as _BaseVectorStore

    HAS_RAG = True
    _rag_backend = "mcp-central-docs"
except ImportError:
    pass

# 2) Fallback: in-repo LanceDB + sentence-transformers (pip install plex-mcp-advanced[rag])
if not HAS_RAG:
    try:
        import lancedb
        from sentence_transformers import SentenceTransformer

        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")

        class LocalVectorStore:
            """In-repo RAG using LanceDB + sentence-transformers. No mcp-central-docs needed."""

            def __init__(self, db_path: str, table_name: str = "plex_media", **kwargs):
                self.db_path = db_path
                self.table_name = table_name
                self.db = lancedb.connect(db_path)
                self._table = None

            def _ensure_table(self, dim: int = 384):
                if self._table is not None:
                    return
                try:
                    self._table = self.db.open_table(self.table_name)
                except Exception:
                    self._table = self.db.create_table(
                        self.table_name,
                        data=[{"id": "", "content": "", "vector": [0.0] * dim, "metadata": {}}],
                        mode="overwrite",
                    )

            def add_documents(self, documents: list, overwrite: bool = True):
                if not documents:
                    return
                texts = [d.get("content", "") or "" for d in documents]
                vectors = _embed_model.encode(texts).tolist()
                rows = []
                for d, vec in zip(documents, vectors, strict=False):
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
                logger.info("Indexed %d documents into local LanceDB", len(rows))

            def search(self, query: str, limit: int = 5, where: Any = None) -> list:
                try:
                    self.db = lancedb.connect(self.db_path)
                    self._table = self.db.open_table(self.table_name)
                except Exception:
                    return []
                qvec = _embed_model.encode([query]).tolist()[0]
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
        self.db_path = db_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../data/lancedb")
        )
        self.vector_store = BaseVectorStore(db_path=self.db_path, table_name="plex_media")
        self.is_available = HAS_RAG

    async def extract_and_index_all(self):
        """Extracts Title, Plot/Summary, Genres, Directors (movies/shows) and artist summaries (music) into LanceDB."""
        reset_rag_sync_progress()
        try:
            return await self._extract_and_index_all_impl()
        except Exception as e:
            logger.exception("RAG extract_and_index_all failed: %s", e)
            _report_progress({"phase": "error", "message": str(e), "indexed_count": 0})
            return 0

    async def _extract_and_index_all_impl(self) -> int:
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
                result = await self.plex.get_library_items(library_id=lib_id, limit=50000)
                items = result.get("items", [])

                for item in items:
                    key = str(item.get("id", item.get("key", "")))
                    title = item.get("title", "")
                    summary = item.get("summary", "")
                    year = item.get("year", "")

                    genres = (
                        list(item.get("genres", [])) if isinstance(item.get("genres"), list) else []
                    )
                    directors = (
                        list(item.get("directors", []))
                        if isinstance(item.get("directors"), list)
                        else []
                    )

                    content = f"Title: {title}\n"
                    if year:
                        content += f"Year: {year}\n"
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

                    doc = {
                        "id": key,
                        "content": content,
                        "metadata": {
                            "title": title,
                            "type": item.get("type", "unknown"),
                            "library": lib_name,
                            "year": safe_year,
                        },
                    }
                    docs.append(doc)
            except Exception as e:
                logger.error("Error extracting items from library %s: %s", lib_name, e)

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

    def semantic_search(self, query: str, limit: int = 5):
        if not self.is_available:
            return []
        return self.vector_store.search(query, limit=limit)
