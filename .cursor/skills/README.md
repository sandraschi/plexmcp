# Agent Skills — plex-mcp Roadmap

Skills for implementing the plex-mcp roadmap. Usable from Cursor,
Claude Code, or Google Antigravity.

## What's here

| Directory                        | Purpose                        |
|----------------------------------|--------------------------------|
| `plex-mcp-roadmap/`              | Orchestrator — shared rules    |

## Per-project implementation guidance

Unlike calibre-mcp where per-project SKILL.md files exist, plex-mcp
delegates directly to the spec files in `docs/plans/`. Each spec is
written in "skill format" — phase-by-phase, with file paths,
schemas, and gotchas. An agent following the roadmap loads:

1. `plex-mcp-roadmap/SKILL.md` (this directory) for shared
   conventions
2. The relevant spec at `docs/plans/{PROJECT}.md`

This avoids duplicating implementation detail between two files.

## Project specs

| Spec                              | Project                     | Effort |
|-----------------------------------|------------------------------|--------|
| `DEEP_METADATA_ENRICHMENT.md`     | Rich per-item metadata       | 3–4 d  |
| `TASTE_MODELLING.md`              | User preference profile      | 2–3 d  |
| `MOOD_PICKER.md`                  | Nightly picker               | 1–2 d  |
| `SUBTITLE_RAG.md`                 | Semantic subtitle search     | 4–5 d  |
| `EPISODE_INTELLIGENCE.md`         | Per-episode context          | 3–4 d  |
| `CROSS_LIBRARY_LINKS.md`          | Cross-library connections    | 2 d    |

## Cross-tool install

### Cursor (default)
Skills are auto-discovered from `.cursor/skills/`.

### Claude Code
```powershell
New-Item -ItemType SymbolicLink -Path "$HOME\.claude\skills\plex-mcp-roadmap" `
  -Target "D:\Dev\repos\plex-mcp\.cursor\skills\plex-mcp-roadmap"
```

### Antigravity (workspace scope)
```powershell
New-Item -ItemType SymbolicLink -Path ".agents\skills" `
  -Target ".cursor\skills"
```

### Gemini CLI
```powershell
robocopy ".\.cursor\skills" "$HOME\.gemini\skills" /E
```

---

Signed: Claude Opus 4.7 (Anthropic), April 2026.
