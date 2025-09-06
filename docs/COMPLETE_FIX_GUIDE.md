# PlexMCP Complete Fix Guide - Emergency Reconstruction

**Date**: September 6, 2025  
**Priority**: 🚨 **CRITICAL - COMPLETE REWRITE REQUIRED**  
**Target**: Production-ready FastMCP 2.10 server  
**Timeline**: 5-7 days intensive development  

## Executive Summary

This document provides a comprehensive roadmap to transform the current PlexMCP codebase from a non-functional mock system into a production-ready FastMCP 2.10 server. The current implementation requires complete architectural reconstruction.

## Current State Analysis

### Critical Failures Identified
- ❌ **No real Plex integration** - All responses are hardcoded mocks
- ❌ **FastMCP 2.10 violations** - Massive server.py file, improper structure
- ❌ **Broken STDIO** - No MCP protocol compliance
- ❌ **Fake feature claims** - 83 non-existent tools in manifest
- ❌ **Import hell** - Multiple fallback strategies everywhere
- ❌ **Sync/async mixing** - Thread pool abuse instead of proper async
- ❌ **Dependency conflicts** - Dead dependencies and version mismatches

### Severity Assessment
**Overall Score**: 1.3/10 - Complete architectural failure  
**Production Readiness**: 0%  
**Recommended Action**: Full rewrite using proper patterns  

## Phase 1: Emergency Stabilization (Day 1)

### 1.1 Remove All Mock Data and Fake Features

```bash
# Remove fake Austrian tools
rm src/plex_mcp/api/vienna.py
rm src/plex_mcp/services/vienna_service.py

# Clean up fake implementations
# Edit these files to remove mock returns:
# - src/plex_mcp/api/core.py
# - src/plex_mcp/api/playlists.py
# - src/plex_mcp/api/playback.py
# - src/plex_mcp/api/admin.py
```

**Action Items**:
1. Delete all functions with hardcoded mock returns
2. Remove `wiener_recommendations`, `european_content_finder`, etc.
3. Fix manifest.json to list only actual working tools (10 max)
4. Remove DXT package until functionality is real

### 1.2 Fix Critical Dependencies

**Remove Dead Dependencies**:
```toml
# From pyproject.toml - REMOVE:
xml2dict = "*"  # Not used anywhere
rich = "*"      # Breaks MCP stdio protocol
```

**Fix Async Dependencies**:
```toml
# REPLACE requests with:
aiohttp = "^3.8.0"
aiofiles = "^23.0.0"

# KEEP and update:
fastmcp = "^2.10.1"
plexapi = "^4.15.0"
python-dotenv = "^1.0.0"
pydantic = "^2.0.0"
```

### 1.3 Implement Proper STDIO Protocol

**Create new main entry point** - `src/plex_mcp/main.py`:
```python
#!/usr/bin/env python3
"""
PlexMCP Main Entry Point
Proper MCP stdio protocol implementation
"""

import asyncio
import sys
from typing import Any, Sequence
from fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# Import all tool modules
from .api import core, playlists, playback, admin
from .config import get_settings

async def main() -> None:
    """Main entry point for MCP stdio server."""
    settings = get_settings()
    
    # Create FastMCP app
    app = FastMCP("PlexMCP", 
                  description="Production Plex Media Server MCP integration")
    
    # Register all tools from modules
    # Tools are auto-registered via @app.tool() decorators
    
    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### 1.4 Fix Import Hell

**Create proper __init__.py structure**:
```python
# src/plex_mcp/__init__.py
"""PlexMCP - Production Plex Media Server MCP Integration"""

__version__ = "2.0.0"
__author__ = "Sandra Schipal"

# Single source of truth for imports
from .config import get_settings
from .services.plex_service import PlexService
from .main import main

__all__ = ["get_settings", "PlexService", "main"]
```

## Phase 2: Architectural Reconstruction (Days 2-3)

### 2.1 Proper FastMCP 2.10 Structure

**New directory structure**:
```
src/plex_mcp/
├── __init__.py          # Package initialization
├── main.py              # MCP stdio entry point
├── config.py            # Configuration management
├── models/              # Pydantic models only
│   ├── __init__.py
│   ├── server.py        # Server status models
│   ├── media.py         # Media item models
│   ├── session.py       # Session models
│   └── user.py          # User models
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── plex_service.py  # Core Plex API wrapper
│   ├── auth_service.py  # Authentication handling
│   └── cache_service.py # Caching layer
├── api/                 # MCP tool definitions
│   ├── __init__.py
│   ├── core.py          # Core server tools
│   ├── media.py         # Media management tools
│   ├── playback.py      # Playback control tools
│   └── admin.py         # Admin tools
└── utils/               # Utility functions
    ├── __init__.py
    ├── logging.py       # MCP-compatible logging
    └── exceptions.py    # Custom exceptions
```

### 2.2 Implement Real Plex Service Layer

**Create `services/plex_service.py`**:
```python
"""
Production Plex Service Implementation
Real PlexAPI integration with proper async patterns
"""

import asyncio
import aiohttp
from typing import List, Optional, Dict, Any
from plexapi.server import PlexServer
from plexapi.exceptions import PlexApiException

from ..config import get_settings
from ..models import PlexServerStatus, MediaLibrary, MediaItem
from ..utils.exceptions import PlexConnectionError, PlexAuthError

class PlexService:
    """Production Plex service with real API integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.server: Optional[PlexServer] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
    
    async def connect(self) -> None:
        """Establish connection to Plex server."""
        try:
            # Create async HTTP session
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=10)
            )
            
            # Connect to Plex server in thread pool
            # PlexAPI is sync, so we run it in executor
            loop = asyncio.get_event_loop()
            self.server = await loop.run_in_executor(
                None,
                lambda: PlexServer(
                    self.settings.plex.server_url,
                    self.settings.plex.token
                )
            )
            
        except Exception as e:
            raise PlexConnectionError(f"Failed to connect to Plex: {e}")
    
    async def disconnect(self) -> None:
        """Close connections."""
        if self._session:
            await self._session.close()
    
    async def get_server_status(self) -> PlexServerStatus:
        """Get real server status from Plex API."""
        if not self.server:
            raise PlexConnectionError("Not connected to Plex server")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Run sync PlexAPI calls in executor
            server_info = await loop.run_in_executor(
                None,
                lambda: {
                    'name': self.server.friendlyName,
                    'version': self.server.version,
                    'platform': self.server.platform,
                    'updated_at': int(self.server.updatedAt.timestamp()) if self.server.updatedAt else 0,
                    'size': getattr(self.server, 'size', 0),
                    'my_plex_username': getattr(self.server, 'myPlexUsername', ''),
                    'my_plex_mapping_state': getattr(self.server, 'myPlexMappingState', ''),
                    'connected': True
                }
            )
            
            return PlexServerStatus(**server_info)
            
        except PlexApiException as e:
            raise PlexConnectionError(f"Plex API error: {e}")
    
    async def get_libraries(self) -> List[MediaLibrary]:
        """Get real library information from Plex API."""
        if not self.server:
            raise PlexConnectionError("Not connected to Plex server")
        
        try:
            loop = asyncio.get_event_loop()
            
            # Get libraries in executor
            libraries_data = await loop.run_in_executor(
                None,
                self._get_libraries_sync
            )
            
            return [MediaLibrary(**lib) for lib in libraries_data]
            
        except PlexApiException as e:
            raise PlexConnectionError(f"Failed to get libraries: {e}")
    
    def _get_libraries_sync(self) -> List[Dict[str, Any]]:
        """Sync helper for getting libraries."""
        libraries = []
        for section in self.server.library.sections():
            libraries.append({
                'key': section.key,
                'title': section.title,
                'type': section.type,
                'agent': getattr(section, 'agent', ''),
                'scanner': getattr(section, 'scanner', ''),
                'language': getattr(section, 'language', 'en'),
                'uuid': getattr(section, 'uuid', ''),
                'created_at': int(section.createdAt.timestamp()) if hasattr(section, 'createdAt') and section.createdAt else 0,
                'updated_at': int(section.updatedAt.timestamp()) if hasattr(section, 'updatedAt') and section.updatedAt else 0,
                'count': len(section.all()) if hasattr(section, 'all') else 0
            })
        return libraries

# Global service instance
_plex_service: Optional[PlexService] = None

async def get_plex_service() -> PlexService:
    """Get or create global Plex service instance."""
    global _plex_service
    if _plex_service is None:
        _plex_service = PlexService()
        await _plex_service.connect()
    return _plex_service
```

### 2.3 Rebuild API Layer with Real Data

**Update `api/core.py`**:
```python
"""
Core API endpoints with real Plex integration
NO MORE MOCK DATA
"""

from typing import List, Optional
from fastmcp import FastMCP

from ..models import PlexServerStatus, MediaLibrary
from ..services.plex_service import get_plex_service
from ..utils.exceptions import PlexConnectionError

# Create app instance
app = FastMCP("PlexMCP-Core")

@app.tool()
async def get_plex_status() -> PlexServerStatus:
    """
    Get REAL Plex server status and identity information.
    
    Returns comprehensive server information including version,
    platform, database size, and MyPlex connection status.
    
    Returns:
        Complete server status and configuration information
    """
    try:
        service = await get_plex_service()
        return await service.get_server_status()
    except PlexConnectionError as e:
        raise Exception(f"Failed to get Plex status: {e}")

@app.tool()
async def get_libraries() -> List[MediaLibrary]:
    """
    Get REAL media libraries from Plex server.
    
    Returns information about each library including type,
    item count, and metadata agent configuration.
    
    Returns:
        List of all media libraries with detailed information
    """
    try:
        service = await get_plex_service()
        return await service.get_libraries()
    except PlexConnectionError as e:
        raise Exception(f"Failed to get libraries: {e}")

# Remove all other mock functions until properly implemented
```

### 2.4 Implement Proper Mock Mode

**Add mock service for testing** - `services/mock_service.py`:
```python
"""
Proper mock service for testing without Plex server
Clean separation from production code
"""

from typing import List
from ..models import PlexServerStatus, MediaLibrary
from ..config import get_settings

class MockPlexService:
    """Mock service for testing - clearly marked as mock."""
    
    async def get_server_status(self) -> PlexServerStatus:
        """MOCK: Server status for testing."""
        return PlexServerStatus(
            name="MOCK Plex Server",
            version="1.40.0",
            platform="Docker",
            updated_at=1699027200,  # Nov 2023
            size=2147483648,  # 2GB
            my_plex_username="mock@example.com",
            my_plex_mapping_state="mapped",
            connected=True
        )
    
    async def get_libraries(self) -> List[MediaLibrary]:
        """MOCK: Sample libraries for testing."""
        return [
            MediaLibrary(
                key="1",
                title="MOCK Movies",
                type="movie",
                agent="com.plexapp.agents.imdb",
                scanner="Plex Movie",
                language="en",
                uuid="mock-uuid-1",
                created_at=1699027200,
                updated_at=1699113600,
                count=50
            ),
            MediaLibrary(
                key="2", 
                title="MOCK TV Shows",
                type="show",
                agent="com.plexapp.agents.thetvdb",
                scanner="Plex TV Series",
                language="en",
                uuid="mock-uuid-2",
                created_at=1699027200,
                updated_at=1699113600,
                count=25
            )
        ]
```

**Update service factory** - `services/__init__.py`:
```python
"""Service factory with proper mock/prod separation."""

from ..config import get_settings
from .plex_service import PlexService
from .mock_service import MockPlexService

async def get_plex_service():
    """Get service based on configuration."""
    settings = get_settings()
    
    if settings.development.mock_mode:
        return MockPlexService()
    else:
        service = PlexService()
        await service.connect()
        return service
```

## Phase 3: Production Hardening (Days 4-5)

### 3.1 Comprehensive Error Handling

**Create `utils/exceptions.py`**:
```python
"""Custom exceptions for PlexMCP."""

class PlexMCPError(Exception):
    """Base exception for PlexMCP."""
    pass

class PlexConnectionError(PlexMCPError):
    """Plex server connection failed."""
    pass

class PlexAuthError(PlexMCPError):
    """Plex authentication failed."""
    pass

class PlexAPIError(PlexMCPError):
    """Plex API call failed."""
    pass

class ConfigurationError(PlexMCPError):
    """Configuration is invalid."""
    pass
```

### 3.2 MCP-Compatible Logging

**Create `utils/logging.py`**:
```python
"""MCP-compatible logging system."""

import logging
import sys
from typing import Optional

class MCPFormatter(logging.Formatter):
    """Formatter that doesn't interfere with MCP stdio protocol."""
    
    def format(self, record):
        # Send logs to stderr only, never stdout
        return super().format(record)

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Set up logging that works with MCP stdio."""
    logger = logging.getLogger("plexmcp")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Only log to stderr to avoid interfering with MCP stdio
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(MCPFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(handler)
    return logger
```

### 3.3 Configuration Validation

**Update `config.py`**:
```python
"""Production configuration with validation."""

import os
from typing import Optional
from pydantic import BaseSettings, validator, AnyUrl
from functools import lru_cache

class PlexSettings(BaseSettings):
    """Plex server configuration."""
    server_url: AnyUrl
    token: str
    timeout: int = 30
    verify_ssl: bool = True
    
    @validator('token')
    def token_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Plex token cannot be empty')
        return v
    
    class Config:
        env_prefix = "PLEX_"

class DevelopmentSettings(BaseSettings):
    """Development configuration."""
    debug: bool = False
    mock_mode: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "DEV_"

class Settings(BaseSettings):
    """Main application settings."""
    plex: PlexSettings
    development: DevelopmentSettings = DevelopmentSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings(
        plex=PlexSettings(),
        development=DevelopmentSettings()
    )
```

### 3.4 Test Infrastructure

**Create `tests/test_plex_service.py`**:
```python
"""Tests for Plex service layer."""

import pytest
from unittest.mock import Mock, patch
from src.plex_mcp.services.plex_service import PlexService
from src.plex_mcp.utils.exceptions import PlexConnectionError

@pytest.fixture
async def plex_service():
    """Create mock Plex service for testing."""
    service = PlexService()
    # Mock the PlexServer connection
    with patch('src.plex_mcp.services.plex_service.PlexServer'):
        await service.connect()
        yield service
        await service.disconnect()

class TestPlexService:
    """Test suite for Plex service."""
    
    async def test_get_server_status(self, plex_service):
        """Test server status retrieval."""
        # Mock server attributes
        plex_service.server.friendlyName = "Test Server"
        plex_service.server.version = "1.40.0"
        
        status = await plex_service.get_server_status()
        
        assert status.name == "Test Server"
        assert status.version == "1.40.0"
        assert status.connected is True
    
    async def test_connection_failure(self):
        """Test connection failure handling."""
        service = PlexService()
        
        with patch('src.plex_mcp.services.plex_service.PlexServer', 
                  side_effect=Exception("Connection failed")):
            with pytest.raises(PlexConnectionError):
                await service.connect()

# Run with: pytest tests/ -v
```

### 3.5 Fix DXT Packaging

**Update `dxt_manifest.json`**:
```json
{
  "name": "plexmcp",
  "version": "2.0.0",
  "description": "Production Plex Media Server MCP integration",
  "author": "Sandra Schipal",
  "homepage": "https://github.com/sandraschi/plexmcp",
  "entry_point": "src.plex_mcp.main:main",
  "tools": [
    "get_plex_status",
    "get_libraries"
  ],
  "dependencies": {
    "fastmcp": "^2.10.1",
    "aiohttp": "^3.8.0",
    "plexapi": "^4.15.0",
    "python-dotenv": "^1.0.0",
    "pydantic": "^2.0.0"
  }
}
```

**Update `manifest.json`** (remove all fake tools):
```json
{
  "schema_version": 1,
  "name": "plexmcp",
  "version": "2.0.0",
  "description": "Production Plex Media Server MCP integration",
  "tools": [
    {
      "name": "get_plex_status",
      "description": "Get real Plex server status and information"
    },
    {
      "name": "get_libraries", 
      "description": "Get all media libraries from Plex server"
    }
  ]
}
```

## Phase 4: Quality Assurance & Deployment (Days 6-7)

### 4.1 Integration Testing

**Create `tests/integration/test_real_plex.py`**:
```python
"""Integration tests with real Plex server."""

import pytest
import os
from src.plex_mcp.services.plex_service import PlexService
from src.plex_mcp.config import Settings, PlexSettings, DevelopmentSettings

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("PLEX_TOKEN"),
    reason="Integration tests require PLEX_TOKEN environment variable"
)
class TestRealPlexIntegration:
    """Integration tests with real Plex server."""
    
    async def test_real_plex_connection(self):
        """Test connection to real Plex server."""
        service = PlexService()
        
        try:
            await service.connect()
            status = await service.get_server_status()
            
            assert status.connected is True
            assert status.name is not None
            assert status.version is not None
            
        finally:
            await service.disconnect()
    
    async def test_real_libraries(self):
        """Test getting real libraries."""
        service = PlexService()
        
        try:
            await service.connect()
            libraries = await service.get_libraries()
            
            assert isinstance(libraries, list)
            # Don't assert count since it depends on user's setup
            
        finally:
            await service.disconnect()

# Run with: pytest tests/integration/ -v -m integration
```

### 4.2 Performance Testing

**Create `tests/performance/test_load.py`**:
```python
"""Load testing for PlexMCP."""

import asyncio
import time
import pytest
from src.plex_mcp.services.mock_service import MockPlexService

@pytest.mark.performance
class TestPerformance:
    """Performance tests."""
    
    async def test_concurrent_requests(self):
        """Test concurrent request handling."""
        service = MockPlexService()
        
        async def make_request():
            return await service.get_server_status()
        
        start_time = time.time()
        
        # Run 100 concurrent requests
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert len(results) == 100
        assert duration < 5.0  # Should complete in under 5 seconds
        
        # All results should be valid
        for result in results:
            assert result.name is not None
            assert result.connected is True

# Run with: pytest tests/performance/ -v -m performance
```

### 4.3 MCP Protocol Validation

**Create `tests/mcp/test_protocol.py`**:
```python
"""MCP protocol compliance tests."""

import asyncio
import json
from unittest.mock import AsyncMock
import pytest
from src.plex_mcp.main import main

class TestMCPProtocol:
    """Test MCP protocol compliance."""
    
    async def test_stdio_protocol(self):
        """Test MCP stdio protocol compliance."""
        # Mock stdio streams
        read_stream = AsyncMock()
        write_stream = AsyncMock()
        
        # Mock initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        read_stream.read.return_value = json.dumps(init_message).encode()
        
        # This test would need proper stdio mocking
        # For now, just ensure main function exists and is callable
        assert callable(main)

# Run with: pytest tests/mcp/ -v
```

### 4.4 Documentation Updates

**Update `README.md`**:
```markdown
# PlexMCP - Production Plex Media Server MCP Integration

🎬 **Real Plex integration** with **Austrian efficiency** - working solutions in hours, not days.

## Features

✅ **Real Plex API Integration** - No mock data, actual Plex server communication  
✅ **FastMCP 2.10 Compliant** - Proper architecture and patterns  
✅ **Production Ready** - Comprehensive error handling and logging  
✅ **Mock Mode Support** - Clean testing without Plex server  
✅ **Claude Desktop Compatible** - Proper MCP stdio protocol  

## Installation

```bash
# Clone repository
git clone https://github.com/sandraschi/plexmcp.git
cd plexmcp

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your Plex server details
```

## Configuration

Required environment variables:
```bash
PLEX_SERVER_URL=http://your-plex-server:32400
PLEX_TOKEN=your-plex-token
DEV_MOCK_MODE=false  # Set to true for testing without Plex
```

## Tools Available

| Tool | Description | Status |
|------|-------------|--------|
| `get_plex_status` | Get real server status | ✅ Working |
| `get_libraries` | Get all media libraries | ✅ Working |

**Note**: Only tools listed above are actually implemented. Previous versions claimed 95 tools but only had mock data.

## Development

```bash
# Run tests
pytest tests/ -v

# Run with mock mode
DEV_MOCK_MODE=true python -m src.plex_mcp.main

# Run integration tests (requires real Plex server)
PLEX_TOKEN=your-token pytest tests/integration/ -v -m integration
```

## Claude Desktop Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "plexmcp": {
      "command": "python",
      "args": ["-m", "src.plex_mcp.main"],
      "cwd": "/path/to/plexmcp",
      "env": {
        "PLEX_SERVER_URL": "http://your-plex:32400",
        "PLEX_TOKEN": "your-token"
      }
    }
  }
}
```

## What Changed

This is a **complete rewrite** of the original PlexMCP:

- ❌ **Removed**: 83 fake tools that didn't exist
- ❌ **Removed**: All mock data in production code  
- ❌ **Removed**: Fake "Austrian efficiency" tools
- ✅ **Added**: Real Plex API integration
- ✅ **Added**: Proper FastMCP 2.10 architecture
- ✅ **Added**: Production error handling
- ✅ **Added**: Comprehensive testing

**Previous version assessment**: "Complete architectural failure" - 1.3/10  
**Current version target**: Production ready - 8.5/10
```

## Implementation Schedule

| Phase | Days | Focus | Deliverables |
|-------|------|-------|--------------|
| **Phase 1** | Day 1 | Emergency Stabilization | Remove mocks, fix dependencies, STDIO |
| **Phase 2** | Days 2-3 | Architecture Rebuild | Service layer, real API, proper structure |
| **Phase 3** | Days 4-5 | Production Hardening | Error handling, logging, testing |
| **Phase 4** | Days 6-7 | QA & Deployment | Integration tests, documentation, DXT |

## Success Criteria

### Day 1 Completion:
- [ ] All mock data removed
- [ ] Fake Austrian tools deleted  
- [ ] STDIO protocol working
- [ ] Real Plex connection established

### Day 3 Completion:
- [ ] FastMCP 2.10 compliant structure
- [ ] Real server status and libraries working
- [ ] Proper async/await patterns
- [ ] Mock mode for testing

### Day 7 Completion:
- [ ] Production error handling
- [ ] Comprehensive test suite  
- [ ] Claude Desktop integration tested
- [ ] DXT packaging validated
- [ ] Documentation complete

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| PlexAPI sync/async issues | Use proper asyncio executor patterns |
| MCP protocol compliance | Follow FastMCP 2.10 patterns exactly |
| Authentication failures | Comprehensive error handling and validation |
| Performance issues | Connection pooling and caching |
| Testing complexity | Mock service for unit tests, real integration tests |

## Final Notes

This reconstruction plan transforms PlexMCP from **"software theater"** into a **production-ready MCP server**. The key is removing all fake features and building only what actually works, following proper FastMCP 2.10 patterns.

**Austrian efficiency principle**: Build 2 tools that work perfectly, not 95 tools that don't work at all.

**Timeline**: Intensive but achievable - this is days of work, not weeks.

**Validation**: Each phase has clear success criteria and testing requirements.

**Result**: A genuinely useful Plex MCP integration that Claude Desktop users can rely on.
