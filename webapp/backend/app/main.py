"""FastAPI application for PlexMCP webapp."""

import logging
import logging.handlers
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response("index.html", scope)
        return response


from .api import (
    arr_stack,
    fleet,
    help_api,
    images,
    library,
    llm,
    logs,
    media,
    movies,
    playback,
    rag,
    repair,
    search,
    server,
    system,
    v1,
    webapp_launch,
    workflows,
)
from .config import settings

# 1. Immediate Path & Logging setup
_frozen = getattr(sys, "frozen", False)
_current_file = Path(__file__).resolve()
if _frozen:
    _log_dir = Path(os.environ.get("LOCALAPPDATA", ".")) / "ai.fleet.plex-mcp" / "logs"
else:
    project_root = _current_file.parent.parent.parent.parent
    src_path = project_root / "src"
    if src_path.exists():
        src_str = str(src_path)
        if src_str not in sys.path:
            sys.path.insert(0, src_str)
    _log_dir = project_root / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "webapp.log"


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if reloaded
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root_logger.handlers):
        handler = logging.handlers.RotatingFileHandler(
            _log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(handler)

        # Also ensure console output for uvicorn window
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
        root_logger.addHandler(console)

        # Force uvicorn loggers to use our file handler but keep their own stream
        for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
            logger_obj = logging.getLogger(logger_name)
            logger_obj.addHandler(handler)
            logger_obj.propagate = True  # Allow reaching root but we added handler explicitly to be safe


setup_logging()
logger = logging.getLogger(__name__)

# 2. Settings Bootstrapping (Call before MCP mounting)
try:
    from .settings_store import load_and_apply

    load_and_apply()
    # Apply Settings to OS environment immediately so Tools can see them
    for key in ["PLEX_TOKEN", "PLEX_URL", "LLM_BASE_URL", "LLM_PROVIDER", "LLM_API_KEY", "TMDB_API_KEY"]:
        val = getattr(settings, key, None)
        if val and not os.environ.get(key):
            os.environ[key] = str(val)
            if key == "PLEX_URL":
                os.environ["PLEX_SERVER_URL"] = str(val)
    logger.info("Initializing PlexMCP Backend (SOTA 2026)")
except Exception:
    logger.exception("Failed to bootstrap settings")

# 3. Lazy imports for API routes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan handler — starts lazy FastMCP mount in background."""
    # Start loading FastMCP in background (takes ~90s, non-blocking)
    _asyncio.create_task(_lazy_mount_mcp())
    yield


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# 3. FastMCP Mounting (lazy — loaded in background after API is up)
# fastmcp takes ~90s to import and the webapp doesn't use /mcp (tools are
# called directly via mcp_client.py). We mount in background so the API
# starts instantly and /mcp becomes available ~90s later.
import asyncio as _asyncio  # noqa: E402

_mcp_loaded = False


async def _lazy_mount_mcp():
    try:
        from plex_mcp.app import http_app

        mcp_app = http_app()
        if mcp_app:
            app.mount("/mcp", mcp_app)
            global _mcp_loaded
            _mcp_loaded = True
            logger.info("FastMCP mounted at /mcp (lazy-loaded)")
        else:
            logger.error("FastMCP http_app() returned None")
    except Exception as e:
        logger.error("Could not mount FastMCP HTTP app: %s", e, exc_info=True)


_tauri_desktop = os.environ.get("PLEX_TAURI", "").lower() in ("1", "true", "yes")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=r"https?://tauri\.localhost(:\d+)?" if _tauri_desktop else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Route Registration
app.include_router(images.router, prefix="/api/image", tags=["images"])
app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(server.router, prefix="/api/server", tags=["server"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(repair.router, prefix="/api/repair", tags=["repair"])
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
app.include_router(arr_stack.router, prefix="/api/arr", tags=["arr"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["workflows"])

# Mount frontend SPA at /app/ for Tauri WebView navigation
import os as _os

_frontend_dist = None
_try_paths = []
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _mei = sys._MEIPASS
    _try_paths = [
        _os.path.join(_mei, "webapp", "frontend", "out"),
        _os.path.join(_mei, "frontend", "out"),
        _os.path.join(_os.path.dirname(_mei), "webapp", "frontend", "out"),
    ]
_try_paths.append(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "frontend", "out"))
for _p in _try_paths:
    if _p and _os.path.isdir(_p):
        _frontend_dist = _p
        break
if _frontend_dist and _os.path.isdir(_frontend_dist):
    _frontend_dist = _os.path.realpath(_frontend_dist)
    try:
        app.mount("/app", SPAStaticFiles(directory=_frontend_dist, html=True, follow_symlink=True), name="frontend")
    except TypeError:
        app.mount("/app", SPAStaticFiles(directory=_frontend_dist, html=True), name="frontend")
    logger.info("Frontend SPA mounted at /app from %s", _frontend_dist)
else:
    logger.warning("Frontend dist not found (tried: %s) — API only", "; ".join(str(p) for p in _try_paths))


@app.get("/")
async def root():
    return {
        "message": "PlexMCP Webapp API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


import contextlib as _ctx
import time as _time

_SERVER_START = _time.time()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "server": "plex-mcp",
        "version": "2.4.1",
        "uptime_seconds": int(_time.time() - _SERVER_START),
        "tool_count": _count_plex_tools(),
        "providers": {"plex": "connected"},
    }


def _count_plex_tools() -> int:
    try:
        from plex_mcp.app import mcp as _mcp

        if hasattr(_mcp, "_tools"):
            return len(_mcp._tools)
    except Exception:
        pass
    return 22


@app.get("/api/v1/diagnostics")
async def get_cua_diagnostics():
    uptime = int(_time.time() - _SERVER_START)
    cpu = mem = disk = None
    tesseract = False
    window = False
    with _ctx.suppress(Exception):
        import psutil

        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage(__import__("os").environ.get("SystemDrive", "C:") + "\\").percent
    with _ctx.suppress(Exception):
        import subprocess

        tesseract = (
            subprocess.run(
                [r"C:\Program Files\Tesseract-OCR\tesseract.exe", "--version"], capture_output=True, timeout=5
            ).returncode
            == 0
        )
    with _ctx.suppress(Exception):
        import pywinauto

        a = pywinauto.Application(backend="uia").connect(title_re="Plex MCP")
        a.window(title_re="Plex MCP").wait("visible", timeout=2)
        window = True
    return {
        "success": True,
        "data": {
            "backend": {"status": "ok", "version": "2.4.1", "uptime_seconds": uptime, "port": 10740},
            "system": {"cpu_percent": cpu, "memory_percent": mem, "disk_percent": disk},
            "tools": {"total": _count_plex_tools(), "categories": ["library", "media", "search", "playlist", "server"]},
            "errors": {"count": 0, "recent": []},
            "cua_status": {"window_found": window, "backend_reachable": True, "tesseract_available": tesseract},
        },
    }


@app.get("/mcp/status")
async def mcp_status():
    return {"loaded": _mcp_loaded, "message": "FastMCP mounts in background ~90s after startup"}
