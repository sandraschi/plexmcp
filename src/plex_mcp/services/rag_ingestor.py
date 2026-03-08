import logging
import os
import sys
from typing import Any

logger = logging.getLogger(__name__)

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
        if not self.is_available:
            logger.error("RAG Core is not available.")
            return 0

        libraries = await self.plex.get_libraries()
        docs = []

        for lib in libraries:
            if lib.get("type") not in ("movie", "show", "artist"):
                continue
            lib_id = str(lib.get("id"))
            lib_name = lib.get("title", "Unknown Library")

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
            # Overwrite=True will completely replace existing metadata which serves as simple delta-sync
            # for the entire table. We can add proper diff logic later if efficiency is required.
            self.vector_store.add_documents(docs, overwrite=True)
            return len(docs)
        return 0

    def semantic_search(self, query: str, limit: int = 5):
        if not self.is_available:
            return []
        return self.vector_store.search(query, limit=limit)
