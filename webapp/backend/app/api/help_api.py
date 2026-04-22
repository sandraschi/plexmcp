"""Help content API for webapp help modal."""

from fastapi import APIRouter, Query

router = APIRouter()

HELP_BASIC = """
# PlexMCP Webapp - Basic

## Overview
- **Overview**: Server status and quick links.
- **Libraries**: List Plex libraries; click to search within one.
- **Search**: Full-text search (query, optional library). Results as JSON.
- **Server**: Plex server info (raw).
- **Chat**: AI chat with local LLM (Ollama/LM Studio). Personalities, prompt refining, export.

## Setup
1. Set PLEX_TOKEN and PLEX_URL in webapp/backend/.env
2. Run: cd webapp; powershell -ExecutionPolicy Bypass -File .\\start.ps1
3. Backend: http://localhost:10740  Frontend: http://localhost:10741
""".strip()

HELP_INTERMEDIATE = HELP_BASIC + """

## Logger modal (topbar)
Shows tail of webapp log file. Use filter/level to narrow. Refreshes on level change.

## Help modal
This content. Levels: Basic, Intermediate, Advanced, Expert.

## Semantic & Dialogue Search
Use Search with natural-language. Toggle between **Metadata** (keyword/context) and **Dialogue** (index subtitles) to find exact scenes and quotes.
""".strip()

HELP_ADVANCED = HELP_INTERMEDIATE + """

## LLM (Chat)
- Provider: Ollama (default http://127.0.0.1:11434) or LM Studio / OpenAI-compatible.
- Set LLM_BASE_URL and optional LLM_API_KEY in backend/.env.
- Personalities set system prompt. "Refine" uses LLM to improve your message before sending.
- Export: download chat as Markdown or JSON.

## Neural RAG (v2.5.0)
Backend can index Plex metadata and **Subtitles** (SRT/VTT). Use the **RAG Dashboard** to trigger reindexes and monitor vector counts.
""".strip()

HELP_EXPERT = HELP_ADVANCED + """

## AI Workflows
POST /api/workflows/run with id (e.g. search_and_summarize) and params. Runs Plex search then LLM summarization.

## API docs
http://localhost:10740/docs
""".strip()


@router.get("")
async def get_help(
    level: str = Query("basic", description="basic | intermediate | advanced | expert"),
):
    """Return help content for help modal."""
    key = level.lower() if level else "basic"
    if key == "expert":
        return {"level": key, "content": HELP_EXPERT}
    if key == "advanced":
        return {"level": key, "content": HELP_ADVANCED}
    if key == "intermediate":
        return {"level": key, "content": HELP_INTERMEDIATE}
    return {"level": "basic", "content": HELP_BASIC}
