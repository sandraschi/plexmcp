import logging
import os
import sys

# Ensure we can import the shared vector store
central_docs_src = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../mcp-central-docs/src")
)
if os.path.exists(central_docs_src) and central_docs_src not in sys.path:
    sys.path.append(central_docs_src)

try:
    from docs_mcp.backend.rag_core import BaseVectorStore

    HAS_RAG = True
except ImportError:
    HAS_RAG = False

    class BaseVectorStore:
        def __init__(self, *args, **kwargs):
            pass

        def add_documents(self, documents, overwrite=True):
            pass

        def search(self, query, limit=5, where=None):
            return []


logger = logging.getLogger(__name__)


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
                        [g for g in item.get("genres", [])]
                        if isinstance(item.get("genres"), list)
                        else []
                    )
                    directors = (
                        [d for d in item.get("directors", [])]
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
