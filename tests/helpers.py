"""Test utilities for unwrapping FastMCP ToolResult / plain dict tool returns."""

from __future__ import annotations

import json
from typing import Any


def tool_payload(result: Any) -> Any:
    """Normalize tool return value to a dict (or pass through) for assertions."""
    if isinstance(result, dict):
        return result
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        return sc
    content = getattr(result, "content", None)
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
    return result
