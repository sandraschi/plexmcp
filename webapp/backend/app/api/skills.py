"""Skills/prompts catalog for the webapp Skills page and chat skill-first prompts.

Static mirror of the MCP prompts/resources registered in
``src/plex_mcp/app.py`` (plex_media_guide, prompt://plex/*, resource://plex/*).
Kept static on purpose: importing plex_mcp.app here would pay the ~90s FastMCP
import inside a request. Update this file when app.py gains prompts/resources.
"""

from fastapi import APIRouter

router = APIRouter()

SKILLS_SOURCE = "src/plex_mcp/app.py (@mcp.prompt / @mcp.resource)"

PROMPTS = [
    {
        "uri": "prompt://plex-media-guide",
        "name": "plex_media_guide",
        "title": "Plex media search guide",
        "description": "Guide for Plex media search and RAG. Use for agentic workflows.",
        "use_when": "Keyword vs semantic search routing for media discovery.",
    },
    {
        "uri": "prompt://plex/rag-workflow",
        "name": "prompt_plex_rag_workflow",
        "title": "RAG workflow",
        "description": "Instructions for metadata sync and semantic query.",
        "use_when": "Indexing the library, then natural-language discovery.",
    },
    {
        "uri": "prompt://plex/agentic-pattern",
        "name": "prompt_plex_agentic_pattern",
        "title": "Agentic pattern",
        "description": "How to invoke agentic_plex_workflow safely.",
        "use_when": "Multi-step tasks via agentic_plex_workflow with real tool execution.",
    },
    {
        "uri": "prompt://plex/library-tour",
        "name": "prompt_plex_library_tour",
        "title": "Library tour",
        "description": "Walkthrough for listing and browsing libraries.",
        "use_when": "First-time exploration of sections and items.",
    },
]

RESOURCES = [
    {
        "uri": "resource://plex/capabilities",
        "title": "Capabilities",
        "description": "Discover tools, sampling, RAG, and agentic entrypoints.",
    },
    {
        "uri": "resource://plex/skills",
        "title": "Skills reference",
        "description": "Expert personas and workflows (Plex expert, anime curator, home theater, semantic discovery, agentic).",
    },
]


@router.get("")
async def list_skills():
    """Skill listing for the Chat page skill-first prompt and the Skills page."""
    return {
        "source": SKILLS_SOURCE,
        "prompts": PROMPTS,
        "resources": RESOURCES,
        "count": len(PROMPTS) + len(RESOURCES),
    }
