"""Test utilities for unwrapping FastMCP ToolResult / plain dict tool returns."""

from __future__ import annotations

import json
from typing import Any


def tool_payload(result: Any) -> Any:
    """Normalize tool return value to a dict (or pass through) for assertions."""
    if isinstance(result, dict):
        return result
    # Conversational content comes first (has operation, success, data)
    content = getattr(result, "content", None)
    if isinstance(content, dict):
        return content
    if content:
        for block in content:
            text = getattr(block, "text", None)
            if text:
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue
    # Fall back to structured_content (Prefab wire JSON, etc.)
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        return sc
    return result
