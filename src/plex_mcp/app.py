"""
Shared FastMCP instance for PlexMCP.

This module creates the central FastMCP instance that all API modules use.
Separating it prevents circular import issues.
"""

from fastmcp import FastMCP

# Create the main FastMCP instance
mcp = FastMCP(name="PlexMCP", version="2.1.0")
