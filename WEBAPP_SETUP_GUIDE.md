# Plex-MCP Webapp Setup Guide

**Quick Start Guide** - Build a FastAPI + Next.js webapp for Plex-MCP without the debugging pain.

> **Note**: For a generalized guide that works for any FastMCP server, see [`mcp-central-docs/docs/patterns/WEBAPP_SETUP_GUIDE.md`](../../mcp-central-docs/docs/patterns/WEBAPP_SETUP_GUIDE.md). This guide is Plex-specific with concrete examples.

## Architecture Overview

```
plex-mcp/
├── src/                    # MCP server source (FastMCP tools)
├── webapp/
│   ├── backend/           # FastAPI HTTP wrapper
│   │   ├── app/
│   │   │   ├── main.py    # FastAPI app + startup initialization
│   │   │   ├── api/       # REST endpoints (one per MCP tool category)
│   │   │   ├── mcp/
│   │   │   │   └── client.py  # MCP client wrapper
│   │   │   ├── config.py  # Settings
│   │   │   └── utils/     # Error handling, etc.
│   │   └── requirements.txt
│   └── frontend/          # Next.js 15 frontend
│       ├── app/           # Next.js App Router pages
│       ├── components/   # React components
│       └── package.json
```

**Key Pattern**: Dual interface - FastMCP HTTP endpoints mounted at `/mcp` (stdio for MCP clients, HTTP for webapp).

## Critical Setup Steps (Do These First!)

### 1. Backend Setup

```powershell
cd webapp\backend

# Create venv
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# CRITICAL: Install plex_mcp in editable mode
pip install -e ../../

# Verify import works
python -c "import plex_mcp; print('SUCCESS')"
```

### 2. Path Configuration (CRITICAL!)

**Problem**: `uvicorn` reloader subprocesses don't inherit `sys.path` correctly.

**Solution**: Set up paths in `main.py` BEFORE any other imports:

```python
"""FastAPI application for Plex webapp."""

import logging
import os
import sys
from pathlib import Path

# CRITICAL: Set up Python path BEFORE any other imports
# This ensures plex_mcp is importable even in uvicorn reloader subprocesses
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent.parent
src_path = project_root / "src"

if not src_path.exists():
    current = _current_file.parent
    while current != current.parent:
        if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
            project_root = current
            src_path = project_root / "src"
            break
        current = current.parent

if src_path.exists():
    src_str = str(src_path)
    # CRITICAL: Set PYTHONPATH environment variable FIRST (for uvicorn subprocesses)
    os.environ["PYTHONPATH"] = src_str
    # Then ensure it's in sys.path
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    elif sys.path.index(src_str) != 0:
        sys.path.remove(src_str)
        sys.path.insert(0, src_str)

# NOW import FastAPI and other dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
```

### 3. MCP Client Setup

**Pattern**: Preload and cache tool functions to avoid import errors.

In `app/mcp/client.py`:

```python
"""MCP client wrapper for calling PlexMCP tools."""

import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional
import httpx

# CRITICAL: Same path setup as main.py
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent.parent
src_path = project_root / "src"

if not src_path.exists():
    current = _current_file.parent
    while current != current.parent:
        if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
            project_root = current
            src_path = project_root / "src"
            break
        current = current.parent

if src_path.exists():
    src_str = str(src_path)
    os.environ["PYTHONPATH"] = src_str
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    elif sys.path.index(src_str) != 0:
        sys.path.remove(src_str)
        sys.path.insert(0, src_str)

# Cache for preloaded tool functions
_tool_cache: Dict[str, Any] = {}

def _preload_tools():
    """Preload all MCP tool functions and cache them."""
    global _tool_cache
    
    # Map tool names to their import paths
    tool_modules = {
        "plex_library": "plex_mcp.tools.library.plex_library",
        "plex_media": "plex_mcp.tools.media.plex_media",
        "plex_server": "plex_mcp.tools.server.plex_server",
        # ... add all your MCP tools here
    }
    
    for tool_name, module_path in tool_modules.items():
        try:
            module = __import__(module_path, fromlist=[tool_name])
            tool_func = getattr(module, tool_name)
            _tool_cache[tool_name] = tool_func
        except (ImportError, AttributeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to preload tool {tool_name}: {e}")

# Preload tools at module import time
_preload_tools()

class MCPClient:
    """Wrapper for MCP client to call PlexMCP tools."""
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool by name."""
        # Check cache first (fast path)
        if tool_name in _tool_cache:
            tool_func = _tool_cache[tool_name]
            try:
                result = await tool_func(**arguments)
                return result if isinstance(result, dict) else {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Fallback: try HTTP (if FastMCP HTTP is mounted)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://127.0.0.1:13100/mcp/call",
                    json={"tool": tool_name, "arguments": arguments},
                    timeout=30.0
                )
                return response.json()
        except Exception as e:
            return {"success": False, "error": f"Tool call failed: {e}"}

# Singleton instance
mcp_client = MCPClient()
```

### 4. Startup Initialization Pattern

**Pattern**: Initialize state at startup, cache for fast access.

In `app/main.py`:

```python
# Global cache for frequently accessed data
_plex_cache: dict = {
    "servers": [],
    "current_server": None,
    "libraries": [],
    "loaded": False
}

@app.on_event("startup")
async def startup_event():
    """Initialize Plex connection and cache data on startup."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Re-check path on startup (uvicorn reloader may reset it)
    # ... (same path setup code as at module level)
    
    try:
        from .mcp.client import mcp_client
        
        # Step 1: Discover Plex servers
        logger.info("Discovering Plex servers...")
        servers_result = await mcp_client.call_tool(
            "plex_server",
            {"operation": "status"}
        )
        
        if servers_result.get("success"):
            # Cache servers list
            global _plex_cache
            _plex_cache = {
                "servers": servers_result.get("servers", []),
                "current_server": servers_result.get("current_server"),
                "loaded": True
            }
            logger.info(f"Found {len(_plex_cache['servers'])} Plex server(s)")
        
        # Step 2: Initialize libraries if server available
        if _plex_cache.get("current_server"):
            libraries_result = await mcp_client.call_tool(
                "plex_library",
                {"operation": "list"}
            )
            if libraries_result.get("success"):
                _plex_cache["libraries"] = libraries_result.get("libraries", [])
                logger.info(f"Cached {len(_plex_cache['libraries'])} libraries")
        
        logger.info("SUCCESS: Plex connection initialized and ready")
        
    except Exception as e:
        logger.error(f"Failed to initialize Plex on startup: {e}", exc_info=True)
        logger.warning("Server will start but Plex operations may fail until manually initialized")

# Fast endpoint for cached data
@app.get("/api/plex/servers/list")
async def get_servers_list():
    """Get cached servers list for dropdown population."""
    global _plex_cache
    return {
        "servers": _plex_cache.get("servers", []),
        "current_server": _plex_cache.get("current_server"),
        "loaded": _plex_cache.get("loaded", False)
    }
```

### 5. FastMCP HTTP Mount

**Pattern**: Mount FastMCP HTTP endpoints directly into FastAPI.

```python
# Mount FastMCP HTTP endpoints BEFORE other routers
# FastMCP HTTP endpoints run on same port 13100 - no port hopping!
# Dual interface: stdio for MCP clients, HTTP for webapp backend
logger = logging.getLogger(__name__)

try:
    from plex_mcp.app import mcp
    # FastMCP 2.13+ provides http_app() method directly
    mcp_app = mcp.http_app()
    if mcp_app:
        app.mount("/mcp", mcp_app)
        logger.info("FastMCP HTTP endpoints mounted at /mcp (dual interface: stdio + HTTP)")
except Exception as e:
    logger.warning(f"Could not mount FastMCP HTTP app: {e}")
    logger.warning("Falling back to direct import mode")
```

### 6. API Router Pattern

**Pattern**: One router file per MCP tool category.

**All Available Portmanteau Tools** (16 total):
- `plex_library` - Library management (list, get, create, update, delete, scan, refresh, optimize, etc.)
- `plex_media` - Media browsing and search (browse, search, get_details, get_recent, update_metadata)
- `plex_server` - Server management (status, info, health, maintenance, restart, update)
- `plex_user` - User management (list, get, create, update, delete, update_permissions)
- `plex_playlist` - Playlist operations (list, get, create, update, delete, add_items, remove_items, get_analytics)
- `plex_streaming` - Playback control (list_sessions, list_clients, play, pause, stop, seek, skip_next, etc.)
- `plex_performance` - Performance and transcoding (get_transcode_settings, get_bandwidth, set_quality, etc.)
- `plex_metadata` - Metadata management (refresh, refresh_all, fix_match, update, analyze, match, organize)
- `plex_organization` - Library organization (organize, analyze, clean_bundles, optimize_database, fix_issues)
- `plex_search` - Advanced search (search, advanced_search, suggest, recent_searches, save_search)
- `plex_reporting` - Analytics and reporting (library_stats, usage_report, content_report, user_activity, etc.)
- `plex_collections` - Collections management (list, get, create, update, delete, add_items, remove_items)
- `plex_quality` - Quality profile management (list_profiles, get_profile, create_profile, update_profile, delete_profile, set_default)
- `plex_integration` - Third-party integrations (list_integrations, vienna_recommendations, european_content, etc.)
- `plex_audio_mgr` - Audio management (get_volume, set_volume, mute, unmute, list_streams, select_stream, handover)
- `plex_help` - Help and discovery (help, list_tools, tool_info, examples)

**Note**: All portmanteau tools use an `operation` parameter (e.g., `{"operation": "list"}`) to specify the action.

Example: `app/api/streaming.py` (for media playback)

```python
"""Streaming/playback control API endpoints."""

from fastapi import APIRouter, Query, Body
from typing import Optional

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

@router.get("/clients")
async def list_clients():
    """List all available Plex clients for playback."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming",
            {"operation": "list_clients"}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)

@router.post("/play")
async def play_media(data: dict = Body(...)):
    """Start playing media on a client (video or audio)."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming",
            {
                "operation": "play",
                "client_id": data.get("client_id"),
                "media_key": data.get("media_key"),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)

@router.post("/pause")
async def pause_playback(client_id: str = Body(...)):
    """Pause playback on a client."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming",
            {
                "operation": "pause",
                "client_id": client_id,
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
```

Example: `app/api/library.py` (for library management)

```python
"""Library management API endpoints."""

from fastapi import APIRouter, Query
from typing import Optional

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

@router.get("/")
async def list_libraries():
    """List all available libraries."""
    try:
        result = await mcp_client.call_tool(
            "plex_library",
            {"operation": "list"}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
```

In `main.py`:

```python
from .api import library, media, server  # ... all your routers

# Include routers
app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(server.router, prefix="/api/server", tags=["server"])
```

### 7. Port Configuration

**CRITICAL**: Use ports 13100+ (never below 13100) to avoid conflicts with calibre webapp (13000-13001).

```python
# backend/app/config.py
class Settings:
    API_PORT: int = 13100  # Must be >= 13100 (calibre uses 13000-13001)
    FRONTEND_PORT: int = 13101  # Must be >= 13100
```

```powershell
# Kill zombie processes before starting
Get-NetTCPConnection -LocalPort 13100 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 13100 --log-level info
```

### 8. Backend Requirements

Create `webapp/backend/requirements.txt`:

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.0.0
httpx>=0.25.0
python-multipart>=0.0.6
python-dotenv>=1.0.1
```

### 9. Frontend Setup

```powershell
cd webapp\frontend
npm install

# Use Turbopack (faster than Webpack)
# In package.json:
# "dev": "next dev --turbo"
npm run dev
```

Frontend runs on http://localhost:13101

## Quick Scaffold Checklist

**Follow these steps in order to scaffold the entire webapp quickly.**

### Step 1: Create Directory Structure

```powershell
cd d:\Dev\repos\plex-mcp

# Create backend structure
New-Item -ItemType Directory -Force -Path webapp\backend\app
New-Item -ItemType Directory -Force -Path webapp\backend\app\api
New-Item -ItemType Directory -Force -Path webapp\backend\app\mcp
New-Item -ItemType Directory -Force -Path webapp\backend\app\utils

# Create frontend structure
New-Item -ItemType Directory -Force -Path webapp\frontend\app
New-Item -ItemType Directory -Force -Path webapp\frontend\components
```

### Step 2: Backend Core Files

**2.1 Create `webapp/backend/requirements.txt`:**
```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.0.0
httpx>=0.25.0
python-multipart>=0.0.6
python-dotenv>=1.0.1
```

**2.2 Create `webapp/backend/app/__init__.py`:**
```python
"""Plex webapp backend package."""
```

**2.3 Create `webapp/backend/app/config.py`:**
```python
"""Configuration for Plex webapp backend."""

import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_TITLE: str = "Plex Webapp API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "HTTP API wrapper for PlexMCP server"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 13100  # Must be >= 13100
    RELOAD: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:13101",
        "http://127.0.0.1:13101",
    ]
    
    # MCP Server configuration
    MCP_USE_HTTP: bool = os.getenv("MCP_USE_HTTP", "false").lower() == "true"
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://127.0.0.1:13100")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

**2.4 Create `webapp/backend/app/utils/__init__.py`:**
```python
"""Utility modules."""
```

**2.5 Create `webapp/backend/app/utils/errors.py`:**
```python
"""Error handling utilities."""

from fastapi import HTTPException


class MCPError(Exception):
    """Base exception for MCP-related errors."""
    pass


def handle_mcp_error(error: Exception) -> HTTPException:
    """Convert MCP errors to HTTP exceptions."""
    if isinstance(error, MCPError):
        return HTTPException(status_code=500, detail=str(error))
    return HTTPException(status_code=500, detail=f"Internal server error: {str(error)}")
```

**2.6 Create `webapp/backend/app/mcp/__init__.py`:**
```python
"""MCP client package."""
```

**2.7 Create `webapp/backend/app/mcp/client.py`:**
```python
"""MCP client wrapper for calling PlexMCP tools."""

import sys
import os
from pathlib import Path
from typing import Any, Dict
import httpx

# CRITICAL: Same path setup as main.py
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent.parent
src_path = project_root / "src"

if not src_path.exists():
    current = _current_file.parent
    while current != current.parent:
        if (current / "setup.py").exists() or (current / "pyproject.toml").exists():
            project_root = current
            src_path = project_root / "src"
            break
        current = current.parent

if src_path.exists():
    src_str = str(src_path)
    os.environ["PYTHONPATH"] = src_str
    if src_str not in sys.path:
        sys.path.insert(0, src_str)
    elif sys.path.index(src_str) != 0:
        sys.path.remove(src_str)
        sys.path.insert(0, src_str)

# Cache for preloaded tool functions
_tool_cache: Dict[str, Any] = {}

def _preload_tools():
    """Preload all MCP tool functions and cache them."""
    global _tool_cache
    
    # Map tool names to their import paths (all 16 portmanteau tools)
    tool_modules = {
        "plex_audio_mgr": "plex_mcp.tools.portmanteau.audio_mgr.plex_audio_mgr",
        "plex_collections": "plex_mcp.tools.portmanteau.collections.plex_collections",
        "plex_help": "plex_mcp.tools.portmanteau.help.plex_help",
        "plex_integration": "plex_mcp.tools.portmanteau.integration.plex_integration",
        "plex_library": "plex_mcp.tools.portmanteau.library.plex_library",
        "plex_media": "plex_mcp.tools.portmanteau.media.plex_media",
        "plex_metadata": "plex_mcp.tools.portmanteau.metadata.plex_metadata",
        "plex_organization": "plex_mcp.tools.portmanteau.organization.plex_organization",
        "plex_performance": "plex_mcp.tools.portmanteau.performance.plex_performance",
        "plex_playlist": "plex_mcp.tools.portmanteau.playlist.plex_playlist",
        "plex_quality": "plex_mcp.tools.portmanteau.quality.plex_quality",
        "plex_reporting": "plex_mcp.tools.portmanteau.reporting.plex_reporting",
        "plex_search": "plex_mcp.tools.portmanteau.search.plex_search",
        "plex_server": "plex_mcp.tools.portmanteau.server.plex_server",
        "plex_streaming": "plex_mcp.tools.portmanteau.streaming.plex_streaming",
        "plex_user": "plex_mcp.tools.portmanteau.user.plex_user",
    }
    
    for tool_name, module_path in tool_modules.items():
        try:
            module = __import__(module_path, fromlist=[tool_name])
            tool_func = getattr(module, tool_name)
            _tool_cache[tool_name] = tool_func
        except (ImportError, AttributeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to preload tool {tool_name}: {e}")

# Preload tools at module import time
_preload_tools()

class MCPClient:
    """Wrapper for MCP client to call PlexMCP tools."""
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool by name."""
        # Check cache first (fast path)
        if tool_name in _tool_cache:
            tool_func = _tool_cache[tool_name]
            try:
                result = await tool_func(**arguments)
                return result if isinstance(result, dict) else {"success": True, "data": result}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # Fallback: try HTTP (if FastMCP HTTP is mounted)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://127.0.0.1:13100/mcp/call",
                    json={"tool": tool_name, "arguments": arguments},
                    timeout=30.0
                )
                return response.json()
        except Exception as e:
            return {"success": False, "error": f"Tool call failed: {e}"}

# Singleton instance
mcp_client = MCPClient()
```

**2.8 Create `webapp/backend/app/api/__init__.py`:**
```python
"""API routers package."""
```

**2.9 Create `webapp/backend/app/api/streaming.py` (CRITICAL for playback):**
```python
"""Streaming/playback control API endpoints."""

from fastapi import APIRouter, Body
from typing import Optional

from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

@router.get("/clients")
async def list_clients():
    """List all available Plex clients for playback."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming",
            {"operation": "list_clients"}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)

@router.post("/play")
async def play_media(data: dict = Body(...)):
    """Start playing media on a client (video or audio)."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming",
            {
                "operation": "play",
                "client_id": data.get("client_id"),
                "media_key": data.get("media_key"),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)

@router.post("/pause")
async def pause_playback(data: dict = Body(...)):
    """Pause playback on a client."""
    try:
        result = await mcp_client.call_tool(
            "plex_streaming",
            {
                "operation": "pause",
                "client_id": data.get("client_id"),
            }
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
```

**2.10 Create `webapp/backend/app/api/library.py`:**
```python
"""Library management API endpoints."""

from fastapi import APIRouter
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

@router.get("/")
async def list_libraries():
    """List all available libraries."""
    try:
        result = await mcp_client.call_tool(
            "plex_library",
            {"operation": "list"}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
```

**2.11 Create `webapp/backend/app/api/media.py`:**
```python
"""Media browsing and search API endpoints."""

from fastapi import APIRouter, Query
from typing import Optional
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

@router.get("/browse")
async def browse_media(
    library_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Browse media in a library."""
    try:
        args = {"operation": "browse", "limit": limit}
        if library_id:
            args["library_id"] = library_id
        result = await mcp_client.call_tool("plex_media", args)
        return result
    except Exception as e:
        raise handle_mcp_error(e)

@router.get("/search")
async def search_media(
    query: Optional[str] = Query(None),
    library_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search for media."""
    try:
        args = {"operation": "search", "limit": limit}
        if query:
            args["query"] = query
        if library_id:
            args["library_id"] = library_id
        result = await mcp_client.call_tool("plex_media", args)
        return result
    except Exception as e:
        raise handle_mcp_error(e)
```

**2.12 Create `webapp/backend/app/api/server.py`:**
```python
"""Server management API endpoints."""

from fastapi import APIRouter
from ..mcp.client import mcp_client
from ..utils.errors import handle_mcp_error

router = APIRouter()

@router.get("/status")
async def get_server_status():
    """Get Plex server status."""
    try:
        result = await mcp_client.call_tool(
            "plex_server",
            {"operation": "status"}
        )
        return result
    except Exception as e:
        raise handle_mcp_error(e)
```

**2.13 Create `webapp/backend/app/main.py` (see Section 2 and 4 for full code):**
- Copy path setup from Section 2
- Copy startup initialization from Section 4
- Copy FastMCP HTTP mount from Section 5
- Include all API routers

**2.14 Create `webapp/backend/start_backend.ps1`:**
```powershell
# Kill zombies
Get-NetTCPConnection -LocalPort 13100 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 2

# Set environment
$env:PYTHONPATH = "d:\Dev\repos\plex-mcp\src"
$env:MCP_USE_HTTP = "false"
$env:PLEX_TOKEN = "your-plex-token-here"  # CRITICAL: Get from Plex Web App
$env:PLEX_SERVER_URL = "http://localhost:32400"  # Optional, defaults to this

# Start server
Set-Location $PSScriptRoot
python -m uvicorn app.main:app --host 0.0.0.0 --port 13100 --log-level info
```

### Step 3: Test Backend

```powershell
cd webapp\backend

# Install dependencies
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install -e ../../

# Test import
python -c "import plex_mcp; print('SUCCESS')"

# Start backend
.\start_backend.ps1

# In another terminal, test endpoints
python -c "import httpx; r = httpx.get('http://127.0.0.1:13100/api/streaming/clients'); print(r.status_code, r.json())"
```

### Step 4: Frontend Scaffold (Minimal)

**4.1 Create `webapp/frontend/package.json`:**
```json
{
  "name": "plex-webapp-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev --turbo -p 13101",
    "build": "next build",
    "start": "next start -p 13101"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

**4.2 Create `webapp/frontend/tsconfig.json`:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**4.3 Create `webapp/frontend/app/page.tsx`:**
```tsx
export default function Home() {
  return (
    <main>
      <h1>Plex Webapp</h1>
      <p>Media browser and playback control</p>
    </main>
  );
}
```

**4.4 Create `webapp/frontend/app/layout.tsx`:**
```tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### Step 5: Verify Complete Setup

```powershell
# Backend should start without errors
cd webapp\backend
.\start_backend.ps1
# Check logs for: "SUCCESS: Plex connection initialized and ready for media playback"

# Frontend should start
cd ..\frontend
npm install
npm run dev
# Visit http://localhost:13101 - should see "Plex Webapp" page

# Test API from browser console (F12):
# fetch('http://127.0.0.1:13100/api/streaming/clients').then(r => r.json()).then(console.log)
```

### Step 6: Next Implementation Steps

1. **Add remaining API routers** (user, playlist, metadata, etc.) - copy pattern from streaming.py
2. **Implement media browser UI** - use `/api/media/browse` and `/api/media/search`
3. **Add client selector** - use `/api/streaming/clients` for dropdown
4. **Implement playback controls** - use `/api/streaming/play` and `/api/streaming/pause`
5. **Add video/audio player** - integrate react-player or Plex Web Player SDK

## Common Pitfalls & Solutions

### ❌ ImportError: No module named 'plex_mcp'

**Cause**: `uvicorn` reloader subprocesses don't inherit `sys.path`.

**Solution**: 
1. Set `PYTHONPATH` environment variable BEFORE starting uvicorn
2. Set paths in `main.py` BEFORE any imports
3. Install in editable mode: `pip install -e ../../`

```powershell
$env:PYTHONPATH="d:\Dev\repos\plex-mcp\src"
uvicorn app.main:app --host 0.0.0.0 --port 13100
```

### ❌ Port Already in Use

**Cause**: Previous server instance not killed.

**Solution**: Always kill zombies first:

```powershell
Get-NetTCPConnection -LocalPort 13100 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
```

### ❌ Plex Server Not Connected

**Cause**: Startup event not completing before requests arrive, or PLEX_TOKEN not set.

**Solution**: 
1. Set `PLEX_TOKEN` environment variable (get from Plex Web App → Settings → Account)
2. Set `PLEX_SERVER_URL` if not using default `http://localhost:32400`
3. Use `startup_event` to verify connection and cache server info
4. Provide fast cached endpoints for UI (servers list, clients list)
5. Log initialization success/failure clearly

### ❌ Slow API Responses

**Cause**: Every request calls MCP tool directly.

**Solution**: 
1. Cache frequently accessed data at startup
2. Provide fast cached endpoints (e.g., `/api/plex/servers/list`)
3. Use direct Python imports (cached) instead of HTTP when possible

### ❌ Unicode Emoji Errors

**Cause**: Emojis break encoding in terminals/logs.

**Solution**: NEVER use Unicode emojis in code/logs. Use text markers:
- `[ERROR]`, `[SUCCESS]`, `[INFO]` instead of emojis

## File Structure Checklist

```
webapp/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app + startup
│   │   ├── config.py            # Settings
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── library.py       # One router per MCP tool category
│   │   │   ├── media.py
│   │   │   └── server.py
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   └── client.py        # MCP client wrapper
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── errors.py         # Error handling
│   ├── requirements.txt
│   ├── README.md
│   └── start_backend.ps1        # Startup script
└── frontend/
    ├── app/                      # Next.js App Router
    ├── components/
    ├── package.json
    └── README.md
```

## Testing Checklist

1. **Backend starts without errors**
   ```powershell
   cd webapp\backend
   # Set Plex credentials first
   $env:PLEX_TOKEN = "your-token-here"
   $env:PLEX_SERVER_URL = "http://localhost:32400"  # Optional, defaults to this
   uvicorn app.main:app --host 0.0.0.0 --port 13100
   # Check logs for: "SUCCESS: Plex connection initialized and ready for media playback"
   ```

2. **Imports work**
   ```powershell
   python -c "import plex_mcp; print('SUCCESS')"
   ```

3. **API endpoints respond**
   ```powershell
   python -c "import httpx; r = httpx.get('http://127.0.0.1:13100/api/plex/servers/list'); print(r.status_code, r.json())"
   ```

4. **Frontend connects to backend**
   - Visit http://localhost:13101
   - Check browser console for API errors
   - Verify dropdowns populate from cached endpoints

## Quick Start Script

Create `webapp/backend/start_backend.ps1`:

```powershell
# Kill zombies
Get-NetTCPConnection -LocalPort 13100 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 2

# Set environment
$env:PYTHONPATH = "d:\Dev\repos\plex-mcp\src"
$env:MCP_USE_HTTP = "false"
# CRITICAL: Set Plex credentials for server connection
$env:PLEX_TOKEN = "your-plex-token-here"  # Get from Plex Web App → Settings → Account
$env:PLEX_SERVER_URL = "http://localhost:32400"  # Optional, defaults to this

# Start server
Set-Location $PSScriptRoot
python -m uvicorn app.main:app --host 0.0.0.0 --port 13100 --log-level info
```

## Key Takeaways

1. **Path setup FIRST** - Always set `PYTHONPATH` and `sys.path` before imports
2. **Preload tools** - Cache tool functions to avoid import errors
3. **Startup initialization** - Cache frequently accessed data at startup
4. **Fast cached endpoints** - Provide `/api/plex/servers/list` for UI dropdowns
5. **Dual interface** - Mount FastMCP HTTP at `/mcp` for webapp, stdio for MCP clients
6. **Ports 13100+** - Never use ports below 13100 (calibre webapp uses 13000-13001)
7. **Kill zombies** - Always kill existing processes before starting
8. **No emojis** - Use text markers `[ERROR]`, `[SUCCESS]` instead

## Next Steps

1. Scaffold backend structure (`app/main.py`, `app/mcp/client.py`, `app/api/*.py`)
2. Implement startup initialization for your specific use case
3. Create API routers for each MCP tool category
4. Scaffold frontend with Next.js 15
5. Test all endpoints before building UI
6. Implement UI components using cached endpoints

## Reference Implementation

See `calibre-mcp/webapp/` for a complete working example:
- `backend/app/main.py` - FastAPI app with startup initialization
- `backend/app/mcp/client.py` - MCP client with tool caching
- `backend/app/api/` - API routers for all MCP tools
- `backend/ENDPOINTS.md` - Complete API documentation
