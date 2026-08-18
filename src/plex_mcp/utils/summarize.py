"""
Readable text summaries for list/status tools.

Prefab UI renders as cards in App-capable hosts (Claude Desktop); hosts that do
not render Apps (opencode TUI) show the ToolResult `content` verbatim. This
helper turns a list of item dicts into a compact human-readable summary so
non-App hosts get something useful instead of a raw JSON array.
"""

from __future__ import annotations


def summarize_items(items: list[dict], kind: str = "item", limit: int = 60) -> str:
    """Build a compact text summary of item dicts (id, title/name, type, count)."""
    total = len(items)
    head = f"{kind}s ({total}):" if total != 1 else f"{kind} (1):"
    if not items:
        return f"No {kind}s."
    lines = [head]
    for i, it in enumerate(items, 1):
        if i > limit:
            lines.append(f"  ... and {total - limit} more")
            break
        title = it.get("title") or it.get("name") or str(it.get("id") or "?")
        meta: list[str] = []
        if it.get("type"):
            meta.append(str(it["type"]))
        if "count" in it and it["count"] is not None:
            meta.append(f"{it['count']} items")
        if it.get("id") is not None:
            meta.append(f"id={it['id']}")
        suffix = f" ({', '.join(meta)})" if meta else ""
        lines.append(f"  {i}. {title}{suffix}")
    return "\n".join(lines)
