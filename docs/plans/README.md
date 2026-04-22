# plex-mcp roadmap plans

Strategic specs for the next phase of plex-mcp development.

**Operations / docs / DX todo (separate from feature specs):**  
[`OPERATIONAL_IMPROVEMENTS.md`](OPERATIONAL_IMPROVEMENTS.md)

Start with **`ROADMAP.md`** — it explains the ordering and why,
then points to individual project specs.

Each spec is self-contained and independent. Build any of them
without reading the others.

| File                              | Project                     | Effort |
|-----------------------------------|------------------------------|--------|
| `ROADMAP.md`                      | Overview and ordering        | —      |
| `DEEP_METADATA_ENRICHMENT.md`     | Rich per-item metadata       | 3–4 d  |
| `TASTE_MODELLING.md`              | User preference profile      | 2–3 d  |
| `MOOD_PICKER.md`                  | Nightly "what to watch"      | 1–2 d  |
| `SUBTITLE_RAG.md`                 | Semantic search over subs    | 4–5 d  |
| `EPISODE_INTELLIGENCE.md`         | Per-episode context for TV   | 3–4 d  |
| `CROSS_LIBRARY_LINKS.md`          | Connections across libraries | 2 d    |

All specs authored by Claude Opus 4.7 (Anthropic), April 2026.
Inspired by the calibre-mcp roadmap pattern — the three-surface
architecture (MCP server + webapp + plugin) is working well there,
and much of the intelligence built into calibre-mcp has video-
library equivalents that Plex itself is unlikely to ship.
