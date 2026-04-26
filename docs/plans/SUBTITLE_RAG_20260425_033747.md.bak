# Subtitle RAG — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Status:** design
**Effort:** 4–5 days
**Priority:** 4 of 6

---

## The premise

50,000 videos. Somewhere in there is the scene Sandra is thinking
of. The character, the line, the exchange — she remembers it but
not which film or episode. Plex can't help. Nobody can.

Subtitle files exist for most of the library (either shipped with
the release or pulled via subtitle-matching tools). Subtitles are
timestamped text. Aligned to runtime. Every line searchable.

Build a semantic search index over all subtitles. Map queries to
specific timecodes in specific videos. Return "play from here"
links.

## What you get when it works

Query: "the scene where the accountant explains money laundering
to the dumb bodyguard"

Response: 3 candidate clips with confidence scores, each with:
- Title + episode identifier
- Timestamp (e.g., 00:42:15)
- Surrounding subtitle text (the actual dialogue)
- Plex deep link that starts playback at that timestamp

Query: "every time character X says 'I am inevitable'"

Response: Every match across the library with clip-level context.

Query: "discussions of Kantian ethics"

Response: Scenes across films and episodes where ethical
philosophy is discussed, with semantic (not keyword) matching.

## What's hard about this

- **Subtitle availability and quality vary enormously.** Some
  videos have perfect SRT files with accurate timecodes. Some have
  machine-transcribed garbage. Some have nothing.
- **Multiple subtitle tracks per video.** English, original
  language, commentary, forced-narrative-only. Picking the right
  one matters.
- **Scene boundaries don't align to subtitle chunks.** A meaningful
  "scene" might span 30 subtitles. Semantic retrieval on
  line-by-line subtitles misses context.
- **False positives.** "Money" appears thousands of times. Query
  needs to surface the right scene, not every mention.
- **Transcription for unsubtitled content** is expensive. Whisper
  on 50k videos at 1x realtime is weeks of compute.

## Approach

### Subtitle source priority

1. **Embedded SRT/ASS/SSA** in the video file (extract via ffmpeg)
2. **Sidecar .srt files** next to the video file
3. **Plex-synced subtitles** from OpenSubtitles (via Plex's built-in)
4. **Transcribe via faster-whisper on 4090** for items with no
   subtitles (on-demand, not bulk)

Never transcribe in bulk as first pass. 50k videos × 2 hours avg
× 0.1x realtime with large-v3 on 4090 = ~833 hours of GPU time.
Transcribe only on-request for specific items user cares about,
and mark them for later.

### Chunking strategy

Per subtitle track:
- Parse into line-level records with start/end timestamps
- Group into "scene chunks" of 30-60 seconds (approx 8-15 subtitle
  lines) with 50% overlap
- Each scene chunk = one embedding row
- Chunk text is the concatenated lines; metadata includes
  timestamp range, speaker (if detectable from ASS styling), and
  video identifier

Scene-level chunking is the key choice. Line-level is too granular
(query "money laundering" matches any line with "money"); chapter-
level is too coarse (a 2-hour film with 10 chapters loses 80% of
specificity). 30-60 seconds hits the sweet spot.

### Embedding model

fastembed's `BAAI/bge-small-en-v1.5` (already a dep) works well
for dialogue. For non-English subtitles, use multilingual variant.

### Storage

```sql
CREATE TABLE IF NOT EXISTS subtitle_index_status (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    plex_rating_key   TEXT NOT NULL UNIQUE,
    subtitle_source   TEXT,   -- 'embedded' | 'sidecar' | 'plex' | 'whisper'
    subtitle_language TEXT,
    subtitle_path     TEXT,
    chunk_count       INTEGER,
    indexed_at        TIMESTAMP,
    last_attempted    TIMESTAMP,
    status            TEXT,   -- 'pending' | 'indexed' | 'failed' | 'no_subs'
    error_message     TEXT,
    duration_seconds  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_subtitle_status ON subtitle_index_status(status);
```

LanceDB table `plex_subtitles` with schema:
- `rating_key` (str)
- `chunk_id` (str, `{rating_key}:{chunk_index}`)
- `text` (str)
- `start_ms` (int)
- `end_ms` (int)
- `speaker` (optional str)
- `language` (str)
- `vector` (fixed-dim float array from fastembed)

At 50k videos avg 600 subtitle chunks each = 30M rows. LanceDB
handles this but it's not tiny. Disk: ~6GB embeddings + indexes.
Manageable.

## Implementation

### Phase 1 — Subtitle extraction service (1 day)

`src/plex_mcp/services/subtitles/extractor.py`:

```python
async def extract_subtitles(rating_key: str) -> SubtitleTrack | None:
    """Try all sources in priority order, return first match."""

    meta = get_plex_media_parts(rating_key)

    # 1. Embedded
    for part in meta.parts:
        streams = get_subtitle_streams(part.file)
        if streams:
            best = select_best_track(streams)
            if best:
                srt_path = extract_with_ffmpeg(part.file, best.stream_index)
                return SubtitleTrack(
                    source='embedded',
                    language=best.language,
                    path=srt_path,
                )

    # 2. Sidecar
    sidecar = find_sidecar_srt(part.file)
    if sidecar:
        return SubtitleTrack(source='sidecar', language=detect_lang(sidecar),
                              path=sidecar)

    # 3. Plex-synced
    plex_subs = get_plex_synced_subs(rating_key)
    if plex_subs:
        return SubtitleTrack(source='plex', ...)

    # 4. Whisper — NOT on-demand in extraction; flagged for later
    return None
```

Best-track selection: prefer English (or user's language), prefer
forced-off, prefer SDH-off unless explicitly wanted, prefer
full-subs over forced-narrative.

### Phase 2 — Chunker + embedder (half day)

`src/plex_mcp/services/subtitles/chunker.py`:

```python
def chunk_subtitles(
    srt_text: str,
    window_seconds: int = 45,
    overlap_fraction: float = 0.5,
) -> list[SubtitleChunk]:
    """Parse SRT, group into overlapping scene chunks."""
    lines = parse_srt(srt_text)
    chunks = []
    window_ms = window_seconds * 1000
    step_ms = int(window_ms * (1 - overlap_fraction))

    for start_ms in range(0, lines[-1].end_ms, step_ms):
        end_ms = start_ms + window_ms
        window_lines = [l for l in lines if l.overlaps(start_ms, end_ms)]
        if len(window_lines) < 2:
            continue  # skip empty chunks
        chunks.append(SubtitleChunk(
            start_ms=start_ms,
            end_ms=end_ms,
            text=' '.join(l.text for l in window_lines),
            line_count=len(window_lines),
        ))
    return chunks
```

`src/plex_mcp/rag/subtitles_rag.py`:

```python
def index_subtitles_for_item(rating_key: str, force: bool = False) -> int:
    track = extract_subtitles(rating_key)
    if not track:
        mark_no_subs(rating_key)
        return 0

    chunks = chunk_subtitles(open(track.path).read())
    embeddings = embed_batch([c.text for c in chunks])

    upsert_to_lancedb('plex_subtitles', chunks, embeddings, rating_key)
    mark_indexed(rating_key, track, len(chunks))
    return len(chunks)


def search_subtitles(
    query: str,
    limit: int = 20,
    library_filter: str | None = None,
    media_type: str | None = None,
) -> list[SubtitleHit]:
    query_embedding = embed_query(query)
    results = lancedb_search('plex_subtitles', query_embedding,
                              limit=limit*3)  # overfetch for dedup

    # Dedup: keep best chunk per (rating_key, ~60s time bucket)
    deduped = dedup_by_time_proximity(results)[:limit]

    # Hydrate with Plex metadata
    return [hydrate_with_plex_meta(hit) for hit in deduped]
```

### Phase 3 — Whisper transcription on-demand (1 day)

`src/plex_mcp/services/subtitles/whisper_transcriber.py`:

Uses `faster-whisper` with large-v3 on CUDA. Not installed by
default — guard with try/import. If not available, transcription
operation returns an actionable error.

```python
async def transcribe_on_demand(rating_key: str) -> SubtitleTrack:
    """Run Whisper on an untranscribed item. Slow but available."""
    meta = get_plex_media_parts(rating_key)
    audio_path = extract_audio_via_ffmpeg(meta.parts[0].file)

    model = get_whisper_model()  # cached singleton
    segments, info = model.transcribe(
        audio_path,
        language=None,  # auto-detect
        word_timestamps=False,
    )

    srt_path = write_srt(segments, f"{rating_key}.srt")
    return SubtitleTrack(source='whisper', language=info.language,
                          path=srt_path)
```

For Sandra's 4090, large-v3 runs at ~8x realtime. A 2-hour film
takes 15 minutes. Acceptable for on-demand. Not acceptable for
bulk — protect the user with a confirm prompt for anything over
30 minutes of estimated time.

### Phase 4 — MCP tools (1 day)

New portmanteau `plex_subtitles`:

| Operation          | Purpose                                         |
|-------------------|--------------------------------------------------|
| `index_item`      | Extract + chunk + embed one item                 |
| `bulk_index`      | Index all items with available subs, progress   |
| `search`          | Semantic search across subtitle chunks           |
| `search_in_item`  | Scoped search within one video                   |
| `find_quote`      | Exact-phrase search (bypass semantic)            |
| `transcribe`      | Run Whisper on unsubbed item (slow!)             |
| `stats`           | Index size, coverage percentage, per-library    |
| `status_list`     | Per-item indexing status                        |

Register in `src/plex_mcp/server.py`.

### Phase 5 — REST endpoints (half day)

```
POST /api/subtitles/index/{rating_key}
POST /api/subtitles/bulk-index                body: {library_filter, max_items}
GET  /api/subtitles/bulk-index/status/{job_id}
GET  /api/subtitles/search?q=&limit=&library=
GET  /api/subtitles/search-in/{rating_key}?q=
GET  /api/subtitles/find-quote?q=             (exact phrase)
POST /api/subtitles/transcribe/{rating_key}   body: {confirm: true}
GET  /api/subtitles/stats
```

### Phase 6 — Frontend (1-2 days)

**`/subtitles/search` — new page**

Query input. Result cards:

```
┌─ Breaking Bad · S04E07 · "Problem Dog" ────────────┐
│                                                     │
│  00:23:14                                           │
│  ─────────────────────────────────                 │
│  "I'm not in danger, Skyler. I AM the danger. A    │
│  guy opens his door and gets shot, and you think   │
│  that of me? No. I am the one who knocks."         │
│                                                     │
│  Match score: 0.89 · Surrounding 15 seconds        │
│                                                     │
│  [Play from here]  [Show full scene]  [Jump in Plex]│
└─────────────────────────────────────────────────────┘
```

"Play from here" opens Plex's web player with timestamp. "Show
full scene" expands context in-place. "Jump in Plex" deep-links to
the Plex desktop/TV app with timestamp (use Plex URL scheme).

Filters: library, media type (movie/show/episode), year range,
runtime, language.

**Book/film detail page integration:**

Add a "Quotes" tab that shows subtitle chunks from this specific
item, searchable. For a 10-episode series, that's all 10 episodes'
subtitles in one searchable view.

**Bulk indexing status:**

Progress dashboard. Per-library indexing coverage. Queue of
pending items. ETA.

## Gotchas

- **SRT parsing quirks.** Real-world SRT files have BOM issues,
  inconsistent encoding, overlapping timecodes, empty chunks.
  Use `pysrt` (robust) rather than hand-rolled parsing.

- **ASS/SSA files need conversion.** ffmpeg can extract SRT from
  these; just pass `-c:s srt` in the extraction.

- **Non-Latin scripts.** Japanese, Chinese, Arabic, Hebrew — the
  default `bge-small-en-v1.5` handles these poorly. For
  multilingual libraries, use `paraphrase-multilingual-MiniLM-L12-v2`
  or similar via fastembed. Configurable per library.

- **Timecode alignment bugs.** Some SRT files are offset from the
  video (e.g., converted from different cuts). If Sandra reports
  "the timecodes are all 5 seconds early," we need a per-item
  offset field in `subtitle_index_status`.

- **SDH/forced subtitle confusion.** SDH (Subtitles for Deaf and
  Hard-of-hearing) have extra content like [DOG BARKING]. Might be
  desired or not. Provide a toggle.

- **Rewatch paranoia.** Sandra might not want spoilery subtitle
  content in a search result for a show she's partway through.
  Show-level setting: "exclude episodes later than my current
  watch progress."

- **Bulk-index memory.** Embedding 30M chunks one at a time is
  slow. Batch of 64 on the 4090 with fastembed's ONNX backend =
  ~100 chunks/second. Total bulk time: ~80 hours wall time if no
  overlap with other GPU work. Run overnight for a week, not one
  big job.

- **Transcription cost in battery life / heat.** On-demand
  transcription puts the 4090 at full tilt. Confirm prompt for
  anything over 30 min estimated.

- **False positives due to ambient noise in Whisper.** Whisper
  sometimes hallucinates dialogue during silent scenes. Mark
  transcribed content as `source='whisper'` so UI can indicate
  lower confidence.

- **LanceDB at 30M rows.** Works fine. But index build takes time.
  Use incremental updates, not full rebuilds.

## Testing

1. Index a single film with known subtitle file — verify chunks,
   embeddings, search works
2. Run a semantic query for an obvious line — should return it
3. Run a semantic query for a concept not literally in the subs —
   should return thematically-relevant chunks (and honestly
   indicate low confidence if nothing matches well)
4. Bulk-index one library overnight
5. Test Whisper on-demand with a short clip (15 min film)

## Update on completion

- CHANGELOG
- docs/plans/README.md
- FLEET_INDEX.md

---

*Signed: Claude Opus 4.7 (Anthropic), April 19, 2026.*
