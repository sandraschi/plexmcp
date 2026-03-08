"""FastAPI application for PlexMCP webapp."""

import logging
import logging.handlers
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    fleet,
    help_api,
    images,
    library,
    llm,
    logs,
    movies,
    playback,
    rag,
    search,
    server,
    system,
    v1,
    webapp_launch,
    workflows,
)
from .config import settings

_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent
src_path = project_root / "src"

if src_path.exists():
    src_str = str(src_path)
    os.environ["PYTHONPATH"] = src_str
    import sys

    if src_str not in sys.path:
        sys.path.insert(0, src_str)

_log_dir = project_root / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "webapp.log"
_handler = logging.handlers.RotatingFileHandler(
    _log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logging.getLogger("uvicorn").addHandler(_handler)
logging.getLogger("uvicorn.error").addHandler(_handler)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load file overrides and set PLEX/LLM env from .env if not already set."""
    from .settings_store import load_and_apply

    load_and_apply()
    if not os.environ.get("PLEX_TOKEN") and settings.PLEX_TOKEN:
        os.environ["PLEX_TOKEN"] = settings.PLEX_TOKEN
    if not os.environ.get("PLEX_URL") and settings.PLEX_URL:
        os.environ["PLEX_URL"] = settings.PLEX_URL
        os.environ["PLEX_SERVER_URL"] = settings.PLEX_URL
    if not os.environ.get("LLM_BASE_URL") and settings.LLM_BASE_URL:
        os.environ["LLM_BASE_URL"] = settings.LLM_BASE_URL
    if not os.environ.get("LLM_PROVIDER") and settings.LLM_PROVIDER:
        os.environ["LLM_PROVIDER"] = settings.LLM_PROVIDER
    if not os.environ.get("LLM_API_KEY") and settings.LLM_API_KEY:
        os.environ["LLM_API_KEY"] = settings.LLM_API_KEY
    yield


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

try:
    from plex_mcp.app import http_app

    mcp_app = http_app()
    if mcp_app:
        app.mount("/mcp", mcp_app)
        logger.info("FastMCP HTTP endpoints mounted at /mcp")
except Exception as e:
    logger.warning("Could not mount FastMCP HTTP app: %s", e)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(server.router, prefix="/api/server", tags=["server"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(playback.router, prefix="/api/playback", tags=["playback"])
app.include_router(images.router, prefix="/image", tags=["images"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(webapp_launch.router, prefix="/api", tags=["webapp-launch"])
app.include_router(fleet.router, prefix="/api", tags=["fleet"])
app.include_router(v1.router, prefix="/api/v1", tags=["v1"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(help_api.router, prefix="/api/help", tags=["help"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "PlexMCP Webapp API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}
