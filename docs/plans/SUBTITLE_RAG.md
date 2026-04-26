# Subtitle RAG — Spec

**Author:** Claude Opus 4.7 (Anthropic), April 2026
**Updated:** Claude Opus 4.7, April 25, 2026
**Status:** design
**Effort:** 5–7 days (revised upward from original 4–5 due to multi-tier scope)
**Priority:** 4 of 6

---

## The premise

50,000 videos. Somewhere in there is the scene Sandra is thinking
of. The character, the line, the exchange — she remembers it but
not which film or episode. Plex can't help. Nobody can.

This spec builds a semantic search index over every video in the
library. The key insight is that a subtitle file is close to a
movie script for dialogue-heavy content. An anime episode is often
almost entirely subtitles. "Before Sunrise" is essentially its SRT
file. The limitation — no scene directions, no action lines — is
real but manageable via three complementary enrichment strategies
described below.

## What you get when it works

Query: **"the scene where the accountant explains money laundering
to the dumb bodyguard"**
→ 3 candidate clips with timestamps, surrounding dialogue, Plex
deep links to play from that exact point.

Query: **"cosy adventurers inn scene"** (anime library)
→ Surfaces episodes with inn/tavern scenes even if no dialogue
ever says the words "cosy" or "inn" — because keyframe visual
description captured the setting.

Query: **"discussions of Kantian ethics"**
→ Semantic match over philosophy across your whole library, not
keyword search.

Query: **"sunny meadow"** (query contains no dialogue at all)
→ Returns outdoor pastoral scenes via visual description, useless
with subtitles alone, works with the multimodal tier.

## The text source problem — and the three tiers

A subtitle SRT captures spoken dialogue. A real screenplay also
has: scene headings (INT. ADVENTURERS INN — NIGHT), action lines
(The party enters. Torches cast long shadows.), parentheticals
(whispering), and character directions. For anime especially —
where the visual vocabulary (battle / slice-of-life / festival /
confession / training montage / cosy inn) is highly distinct and
often carries more meaning than dialogue — the SRT alone is a
weak source.

There are three tiers of text enrichment, each broader than the
last:

### Tier 1 — Subtitle text (dialogue only)

Coverage: ~65–70% of the library (embedded or sidecar files).

**Sources in priority order:**

1. **Screenplay from script database** — where available, this is
   the richest text source. See "Script databases" below.
2. **Embedded SRT/ASS/SSA** in MKV/MP4 container (extract via
   ffmpeg)
3. **Sidecar .srt files** alongside the video file
4. **Plex-synced subtitles** from OpenSubtitles (via Plex's built-in
   download)
5. **Whisper transcription** of main audio track — on-demand only
   (see Phase 3)

**Script databases worth fetching from:**

Several sources provide actual screenplay text free online, matchable
to library items via TMDB ID:

- **IMSDb** (imsdb.com) — largest free collection, HTML format,
  ~1,500–2,000 scripts, Hollywood mainstream
- **Daily Script, SimplyScripts, Script Slug, Drew's Script-o-Rama**
  — partial overlapping collections
- **GitHub: Aveek-Saha/Movie-Script-Database** — aggregates all of
  the above with TMDB ID matching already done. Best starting point.

Coverage: roughly 10–15% of library items, heavily biased toward
English-language Hollywood. Foreign cinema, anime, arthouse, older
films — coverage drops sharply. Index as Tier 1+ whenever
available; fall back to SRT otherwise.

Screenplay text is categorically better than SRT for RAG because
it includes scene headings, action, and setting. "The party enters
a rustic tavern" is in the screenplay; it is not in the SRT.

### Tier 2 — Audio Description track

Coverage: ~30–40% of the library (mostly Blu-ray rips, some
streaming rips).

**What it is:** Audio Description (AD) is a legally-mandated
accessibility track on most commercial Blu-ray releases and
streaming content. A professional voiceover narrator describes
visual elements between dialogue: actions, settings, body language,
scene changes. It lives as a separate audio stream in the MKV
container, labelled variously as "Audio Description," "Descriptive
Audio," "AD," or "English AD."

**Why it matters for RAG:** The AD narration is approximately what
a screenplay's action lines contain. "Simba dangles from Rafiki's
arms, looking small and scared" — that's an AD line. Combined with
the dialogue SRT, it gets close to a full screenplay for anything
that has an AD track.

**How to extract it:** ffprobe identifies the AD audio stream by
its title tag or descriptor. ffmpeg extracts it as a separate audio
file. Whisper transcribes it. The result is a timestamped narration
track that can be interleaved with the SRT.

```bash
# Detect AD tracks
ffprobe -v quiet -print_format json -show_streams movie.mkv \
  | jq '.streams[] | select(.codec_type=="audio") | {index, tags}'

# Extract AD audio stream (index found above)
ffmpeg -i movie.mkv -map 0:a:2 -c:a pcm_s16le ad_track.wav

# Transcribe with Whisper
faster-whisper ad_track.wav --model large-v3 --output_format srt
```

AD track detection heuristic: stream title contains any of
"description", "descriptive", "AD", "audio desc" (case-insensitive),
OR stream has `disposition.visual_impaired = 1`.

For anime: AD tracks are rare on Japanese releases. The multimodal
tier (below) covers this gap.

**Interleaving SRT + AD:** Merge the two SRT files by timestamp,
marking each line as `source: 'dialogue'` or `source: 'ad'`.
Chunks are then "the dialogue and description in this 45-second
window combined." Richer than either alone.

### Tier 3 — Keyframe visual description via vision LLM

Coverage: any video for which a vision LLM can be run. Potentially
100% of library given time.

**The core insight (Sandra's observation):** For anime and any
visually-categorical content, the subtitle SRT is missing an entire
dimension. The scene says "We'll rest here for the night" — but
the frame shows a cosy wooden inn with lantern light and armored
travelers. The subtitle cannot be searched for "sunny meadow" or
"adventurers inn." A vision LLM looking at the keyframe can.

**Architecture:**

For each subtitle chunk (45-second window), extract a single
representative keyframe at the chunk midpoint:

```bash
ffmpeg -i episode.mkv -ss 00:14:22.500 -vframes 1 -q:v 2 frame.jpg
```

Pass the frame to a local vision LLM (LLaVA 1.6, or any
vision-capable model on Ollama) with a prompt:

```
Describe this video frame in 2-3 sentences, focusing on:
- Setting and location (interior/exterior, type of place)
- Mood and atmosphere (lighting, weather, time of day)
- What is happening (action, character positions)
- Visual style (if anime: note the art style, any distinctive visual markers)
Be specific and concrete. Do not describe what characters are saying.
```

Generated description is appended to the chunk text before embedding:

```
[Dialogue]
We'll rest here for the night. The innkeeper has a room for us.

[Scene]
Interior of a fantasy tavern. Stone walls with mounted torches casting
warm golden light. A wooden bar with several pewter mugs. Three armored
travelers are seated at a rough-hewn table. Cosy, rustic atmosphere.
Anime art style with detailed background illustration.
```

The combined text is what gets embedded. Now "cosy inn" and
"adventurers inn" and "warm tavern" all match this chunk
semantically, even though the dialogue never said any of those
words.

**Vision model options:**

- **LLaVA 1.6 7B via Ollama** — already available if Ollama is
  running; ~2-3 seconds per frame on 4090; free; handles anime
  well enough
- **Gemini 2.0 Flash (multimodal) via API** — faster, better
  quality, ~$0.0001 per image; at 32 frames per 24-min episode,
  200 episodes = 6,400 frames = $0.64 per series. Negligible.
- **Anime-specific CLIP (e.g., Danbooru-pretrained)** — alternative
  approach: visual embedding rather than description. Produces a
  visual vector that can be queried with text via CLIP's joint
  embedding space. More powerful but requires a separate vector
  index and joint-embedding query path.

**Recommended approach:** LLaVA 1.6 locally for bulk processing;
offer Gemini Flash as quality upgrade for individual series the
user flags as important (e.g., the anime collection).

**Cost model for the anime library:**

Assume 500 anime series × 26 episodes avg × 32 chunks per episode
= 416,000 keyframe descriptions. At 2.5s each on 4090 = ~290 hours
of GPU time total. Spread over many evenings it's tractable.
LLaVA Ollama is free. If using Gemini Flash API: 416k frames ×
$0.0001 = $41.60 one-time. Worth it.

**Visual description as a separate metadata column:**

Store the generated description separately from the dialogue so
the UI can display it and the user can understand why a match was
found. Search result card shows:

```
[Scene at 00:14:22]  ← Adventurers Inn · Episode 7
Dialogue: "We'll rest here for the night."
Scene: Interior fantasy tavern, warm torch lighting, armored travelers
       at table. Cosy rustic atmosphere.
Match: "adventurers inn" → scene description
```

**Schema addition:**

```sql
-- Add to subtitle_index_status:
ALTER TABLE subtitle_index_status
  ADD COLUMN visual_description_status TEXT DEFAULT 'pending';
  -- 'pending' | 'indexed' | 'failed' | 'skipped'
ALTER TABLE subtitle_index_status
  ADD COLUMN visual_description_model TEXT;
```

LanceDB table adds `scene_description` (str) and `visual_vector`
(optional, for CLIP path) fields.

---

## Revised source priority chain

For each library item, the indexer attempts in order:

```
1. Screenplay text (TMDB match via script databases)
   → If found: index as rich text, mark screenplay=true
   → Still extract SRT for timecode alignment

2. AD audio track → Whisper transcription
   → If found: merge with SRT by timestamp

3. Embedded/sidecar/Plex-synced SRT
   → Core baseline for most of library

4. Keyframe visual descriptions (Tier 3)
   → Runs as a separate background pass over already-indexed items
   → Does not block the dialogue index from being available
   → Adds visual dimension incrementally

5. Whisper on main audio
   → On-demand only for items with no text source at all
```

The visual description pass (step 4) is separate from the initial
text indexing. Text indexing runs first and makes the library
searchable quickly. Visual description enriches it over time.

---

## Revised data model

```sql
CREATE TABLE IF NOT EXISTS subtitle_index_status (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    plex_rating_key             TEXT NOT NULL UNIQUE,
    media_type                  TEXT,   -- 'movie' | 'episode' | 'other'
    has_screenplay              INTEGER DEFAULT 0,
    subtitle_source             TEXT,
    -- 'screenplay' | 'embedded' | 'sidecar' | 'plex' | 'whisper' | 'ad+srt'
    subtitle_language           TEXT,
    subtitle_path               TEXT,
    ad_track_detected           INTEGER DEFAULT 0,
    ad_whisper_path             TEXT,
    chunk_count                 INTEGER,
    visual_description_status   TEXT DEFAULT 'pending',
    -- 'pending' | 'indexed' | 'failed' | 'skipped'
    visual_description_model    TEXT,
    visual_description_count    INTEGER,
    indexed_at                  TIMESTAMP,
    last_attempted              TIMESTAMP,
    status                      TEXT,
    -- 'pending' | 'indexed' | 'failed' | 'no_subs'
    error_message               TEXT,
    duration_seconds            INTEGER
);

CREATE INDEX IF NOT EXISTS idx_subtitle_status
    ON subtitle_index_status(status);
CREATE INDEX IF NOT EXISTS idx_subtitle_visual
    ON subtitle_index_status(visual_description_status);
```

LanceDB table `plex_subtitles`:

```python
@dataclass
class SubtitleChunk:
    rating_key: str
    chunk_id: str           # {rating_key}:{chunk_index}
    text: str               # dialogue (+ AD narration if available)
    scene_description: str  # vision LLM output, empty if not run
    start_ms: int
    end_ms: int
    speaker: str | None
    language: str
    source: str             # 'screenplay' | 'srt' | 'ad+srt' | 'whisper'
    has_visual: bool        # True if scene_description populated
    vector: list[float]     # embedding of text + scene_description combined
```

---

## Implementation — revised phases

### Phase 1 — Script database fetcher (half day)

New: `src/plex_mcp/services/subtitles/screenplay_fetcher.py`

Fetch screenplay text from IMSDb and aggregators, match to library
via TMDB ID. Cache in `%APPDATA%\plex-mcp\screenplays\{tmdb_id}.txt`.

Priority pass: run this across the library before anything else.
For matched films, the screenplay text is the index input; the SRT
is used only for timecode alignment (match screenplay text to
timestamps via dialogue matching).

### Phase 2 — AD track detection and extraction (half day)

New: `src/plex_mcp/services/subtitles/ad_extractor.py`

`detect_ad_track(file_path) -> int | None` — returns stream index.
`extract_ad_audio(file_path, stream_index) -> Path` — extracts wav.
`transcribe_ad_audio(wav_path) -> Path` — Whisper → SRT.
`merge_srt_files(dialogue_srt, ad_srt) -> list[MergedLine]` — interleave
by timestamp, tag each line's source.

### Phase 3 — Subtitle extraction service (1 day)

`src/plex_mcp/services/subtitles/extractor.py` — unchanged from
original spec. Handles embedded/sidecar/plex/whisper paths.

**Best-track selection:** prefer English (or user's language),
`disposition.forced == 0`, `disposition.hearing_impaired == 0`
unless SDH explicitly preferred, full subs over forced-narrative.
If ASS/SSA: ffmpeg converts to SRT inline.

**Encoding detection:** use `charset-normalizer` before parsing.
Handles UTF-8, UTF-8-BOM, Latin-1, CP1252, UTF-16. `pysrt` with
`encoding='auto'` is the fallback.

**PGS (bitmap subtitles):** detect via codec_name == 'hdmv_pgs_subtitle'.
Queue for OCR (`pgsrip` + `tesseract`) or mark as Whisper candidate.
Don't block the rest of the pipeline.

### Phase 4 — Chunker + text embedder (half day)

`src/plex_mcp/services/subtitles/chunker.py` — unchanged from
original spec. 45-second overlapping windows.

Embedding input is `chunk.text + '\n\n' + chunk.scene_description`
(empty string for scene_description before visual pass runs).
This means embeddings improve automatically when the visual pass
adds descriptions — but only if we re-embed. Strategy: mark chunks
with `has_visual=False` initially; re-embed in bulk after visual
pass completes. Two-pass approach.

**Embedding model:**
- English-heavy library: `BAAI/bge-small-en-v1.5` (fast, good)
- Multilingual (anime dialogue in Japanese): `paraphrase-multilingual-MiniLM-L12-v2`
- Configurable per library in settings

### Phase 5 — Vision LLM keyframe describer (1-2 days)

New: `src/plex_mcp/services/subtitles/vision_describer.py`

```python
async def describe_keyframe(
    video_path: str,
    midpoint_ms: int,
    model: str = 'llava:7b',   # or 'gemini-2.0-flash'
) -> str:
    """Extract keyframe at midpoint, generate scene description."""

    frame_path = extract_frame_ffmpeg(video_path, midpoint_ms)
    description = await call_vision_model(frame_path, model)
    return description


async def describe_chunks_for_item(
    rating_key: str,
    model: str = 'llava:7b',
    batch_size: int = 8,       # parallel frame extractions
) -> int:
    """Run vision descriptions for all chunks of one item."""

    chunks = get_chunks_without_visual(rating_key)
    video_path = get_video_path(rating_key)

    for batch in batched(chunks, batch_size):
        descriptions = await asyncio.gather(*[
            describe_keyframe(video_path, c.midpoint_ms, model)
            for c in batch
        ])
        update_chunk_descriptions(batch, descriptions)

    # Trigger re-embedding for updated chunks
    re_embed_chunks(rating_key)
    mark_visual_indexed(rating_key, model, len(chunks))
    return len(chunks)
```

**Concurrency notes:**

- Frame extraction (ffmpeg subprocess) is I/O bound; 8 parallel is safe
- LLaVA inference is GPU-bound; limit to 2–4 parallel on 4090 while
  other models might also be running
- Gemini Flash API: 60 req/min limit; use semaphore of 50 with 1s
  spacing

**Prompt engineering:**

The prompt matters. Too generic ("describe this image") produces
useless output. The spec prompt above is the starting point; tune
for anime vs live-action. For anime, add: "Note any anime-specific
visual elements: chibi style, speed lines, emotional reaction
expressions (sweat drop, blush), magical effects, fantasy/sci-fi
setting elements."

### Phase 6 — Whisper on-demand (half day)

`src/plex_mcp/services/subtitles/whisper_transcriber.py` — unchanged
from original spec.

`faster-whisper` large-v3, CUDA, ~8x realtime on 4090. On-demand
only. Confirm prompt for >30min estimated. Marks `source='whisper'`
for lower-confidence UI indicator.

### Phase 7 — MCP tools (1 day)

Extended portmanteau `plex_subtitles`:

| Operation                  | Purpose                                         |
|---------------------------|--------------------------------------------------|
| `index_item`              | Full pipeline for one item (text + optional visual) |
| `bulk_index`              | Text-only pass over whole library, progress      |
| `bulk_visual`             | Visual description pass (after text indexed)     |
| `search`                  | Semantic search, optional visual-only filter     |
| `search_in_item`          | Scoped search within one video                   |
| `find_quote`              | Exact-phrase search                              |
| `transcribe`              | Whisper on-demand for one item                   |
| `describe_item`           | Vision pass for one item only                    |
| `stats`                   | Coverage by tier, by library                     |
| `status_list`             | Per-item status across all tiers                 |
| `fetch_screenplay`        | Try screenplay database fetch for one item       |
| `bulk_fetch_screenplays`  | Screenplay fetch pass over matched library items |

### Phase 8 — REST endpoints (half day)

```
POST /api/subtitles/index/{rating_key}        body: {include_visual?}
POST /api/subtitles/bulk-index               body: {library_filter, max_items}
POST /api/subtitles/bulk-visual              body: {model, max_items}
GET  /api/subtitles/bulk-index/status/{job_id}
GET  /api/subtitles/search?q=&limit=&library=&visual_only=
GET  /api/subtitles/search-in/{rating_key}?q=
GET  /api/subtitles/find-quote?q=
POST /api/subtitles/transcribe/{rating_key}   body: {confirm: true}
POST /api/subtitles/describe/{rating_key}     body: {model?}
GET  /api/subtitles/stats
```

### Phase 9 — Frontend (1–2 days)

**`/subtitles/search` — enhanced result cards:**

```
┌─ Spice and Wolf · S01E03 · "Wolf and Looming Danger" ──┐
│                                                          │
│  [▶ keyframe thumbnail]  00:08:47                        │
│  ──────────────────────────────────                     │
│  "This inn is renowned for its mutton stew."             │
│                                                          │
│  Scene: Interior of a medieval-style tavern. Stone walls │
│  and low wooden beams. Warm candlelight. A silver-haired │
│  girl with wolf ears sits across a table. Anime style.   │
│                                                          │
│  Match via: scene description · score 0.84               │
│                                                          │
│  [▶ Play from here]  [Show scene]  [Jump in Plex]        │
└──────────────────────────────────────────────────────────┘
```

Show keyframe thumbnail inline in search results (extracted and
cached as JPEG by the visual description step — already on disk).

"Match via" badge distinguishes:
- `dialogue` — match was in the spoken text
- `scene description` — match was in the visual description
- `screenplay` — match was in action/setting text from script
- `audio description` — match was in the AD narration

This transparency matters: if Sandra gets a weird result, she
knows why.

**Visual coverage indicator on library pages:**

Small badge on each item showing indexing tier:
`📝` text only · `🖼` text + visual · `📜` screenplay · `🎭` AD track

---

## Gotchas (revised and extended)

**SRT encoding hell.** Use `charset-normalizer` before parsing.
`pysrt` with `encoding='auto'` as fallback. UTF-8-BOM is common
from older Windows subtitle tools.

**ASS/SSA speaker attribution.** ASS format sometimes encodes
speaker in style name. Extract before converting to SRT — it's
the basis for character-voice tracking and "find all X's dialogue."

**AD track false detection.** "English [Audio Description]" in
Plex's track title is reliable. Disposition flags less so. False
AD detection (picking a director commentary track by mistake)
produces bad narration. Validate: AD tracks should have silence
periods exactly where dialogue is, and narration where dialogue
isn't. Simple energy-level heuristic can confirm.

**Vision LLM hallucination.** LLaVA sometimes describes things
not in the frame, especially in dark scenes. Partially mitigated
by the description prompt being concrete ("describe what you can
actually see"). Mark low-confidence descriptions (< 30-word output,
or output starting with "I cannot" / "It's difficult") as
`description_quality='low'` — still indexed but UI shows lower
confidence.

**Anime-specific:** Japanese subtitle files from fansubs are often
higher quality than the official English dub/sub on disc. Plex
may not surface them. Worth checking for `.ja.srt` or `[JA]` sidecar
files in the episode directory.

**Timecode drift.** Some SRT files are offset (e.g., by 23.976 vs
25fps conversion). Per-item timecode offset field in
`subtitle_index_status`. Auto-detect by comparing SRT timing against
Whisper spot-check on known dialogue.

**Bulk visual cost on 4090.** LLaVA 2-3s/frame. Full library 50k
items × 600 chunks = 30M frames, but visual pass is optional per
library. Run it on the anime collection first (highest value);
leave live-action for later unless screenplays or AD tracks are
absent.

**Re-embedding after visual pass.** After visual descriptions are
added to chunks, their embeddings need to change (they now include
scene description text). Two-phase: (1) embed with text only as
`vector_v1`; (2) after visual pass, embed combined text as `vector_v2`.
LanceDB supports multiple vector columns — keep both during transition,
swap default query vector to v2 once visual coverage is adequate.

**Storage at scale.** 30M chunks × ~4KB (text + description + metadata)
= ~120GB SQLite. That's too much for row storage. Keep only the
LanceDB vectors + metadata; store raw subtitle text in per-item
cached files, not in the row. LanceDB handles the search; fetch raw
text by rating_key + chunk_index from the cached SRT file.

---

## Testing

1. Index one dialogue-heavy film (text only) — query for an obvious
   line, verify timestamp accuracy
2. Index one anime episode (text only) — query for thematic content;
   observe that purely visual queries ("sunny meadow") return nothing
3. Run visual pass on same episode — re-embed — query "sunny meadow"
   and "adventurers inn"; verify results appear
4. Index a Blu-ray rip with AD track — verify AD content appears in
   chunk text; query a described action
5. Index a film with screenplay match — verify action lines are
   searchable ("runs toward the burning building")
6. Bulk-index one library overnight; check stats for coverage
7. Spot check timecodes: "play from here" should start within 2s of
   the matched line

---

## What this enables, accumulated

Once all tiers are populated for the anime library:

- **"Find the inn scene in any isekai show"** → visual descriptions match
- **"Find every time a character cries in the rain"** → visual + dialogue
- **"Find philosophical monologues"** → dialogue semantic match
- **"Find every training montage"** → visual descriptions match
- **"Find the scene where they first use the magic sword"** → dialogue match
- **"Sunny meadow opening scenes"** → pure visual match
- **"Character X's dialogue in season 3"** → speaker-tagged dialogue match
  (if ASS speaker tags extracted)

None of these are possible with keyword search. All of them are.

---

## Update on completion

- CHANGELOG
- docs/plans/README.md
- FLEET_INDEX.md
- Note ffmpeg, faster-whisper, LLaVA (via Ollama) as new
  prerequisites in README

---

*Initial spec: Claude Opus 4.7 (Anthropic), April 19, 2026.*
*Updated with three-tier text sources, AD track extraction, screenplay
databases, multimodal keyframe visual descriptions: Claude Opus 4.7,
April 25, 2026.*
