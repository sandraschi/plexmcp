# Building a Plex library (folders, naming, agents, legality, automation)

How to go from files on a disk to a clean, matchable, maintainable Plex
library — and where those files may legally come from. Companion to the
token/setup walkthrough in [ONBOARDING.md](ONBOARDING.md).

> **Not legal advice.** Ripping and downloading rules differ by country and
> change over time. The legal section below is general information for
> orientation only — when in doubt, check your local law or ask a lawyer.

## 1. Plan the shelves first

Create one Plex library per media kind, each rooted at its own folder tree.
Do not mix movies and shows in one folder — agents match per-type and mixed
trees are the top cause of wrong matches.

| Library | Folders | Plex type |
|---|---|---|
| Movies | `Movies/` | movie |
| TV Shows | `TV/` (or `Shows/`) | show |
| Music | `Music/` | artist |
| Photos / home video | `Photos/`, `Home/` | photo |

Keep a separate **staging/inbox folder** outside all libraries
(`Incoming/`) for unsorted arrivals. Files land there, get renamed and
checked, then move into the real trees. Plex never scans `Incoming/`, so
half-named files never pollute matches.

## 2. Folder and file naming (what Plex actually parses)

Plex matches on folder/file names before anything else. Follow its
conventions and most titles match on first scan.

**Movies** — one folder per film, year always included:

```
Movies/
  Stalker (1979)/
    Stalker (1979).mkv
  Mulholland Drive (2001)/
    Mulholland Drive (2001).mp4
```

Editions and quality tags go in braces after the year, never instead of it:
`Blade Runner (1982) {Final Cut}/`, extras in `Featurettes/` or
`Behind The Scenes/` subfolders. Multi-part files:
`Title (Year) - part1.mkv`, `- part2.mkv`.

**TV** — show folder, `Season NN` subfolders, `SxxEyy` in every filename:

```
TV/
  Severance/
    Season 01/
      Severance - S01E01.mp4
      Severance - S01E02.mp4
    Season 02/
      Severance - S02E01.mp4
```

Specials live in `Season 00/` as `S00E01`, `S00E02`. Absolute-numbered
anime also works with the season layout — prefer it, because Plex orders by
season/episode numbers, not filenames. Date-based shows (talk shows, news):
`Show/Season 2024/Show - 2024-03-01.mp4`.

**Music** — `Music/Artist/Album/NN - Title.flac`. Plex reads embedded tags
first, so tagged files survive imperfect folder names; untagged files do not.

Characters to avoid in names: `? * : < > | "` and trailing dots/spaces
(Windows strips them and Plex sees a different string than your ripper
wrote). Prefer ASCII punctuation; Plex normalizes the rest.

## 3. Agents, scanners, and the first scan

When creating the library in Plex (Settings → Manage → Libraries → Add),
pick the matching agent (Plex Movie / Plex TV Series for new setups) and
the matching scanner. Language matters for metadata: set it to the language
you browse in, or titles arrive in the wrong one.

After pointing the library at its folder: **Scan Library Files**, then wait.
First scans of big trees take a while; watch activity, not the clock. Then:

1. `plex_library(operation="list")` — confirm the section exists with the
   right type.
2. Browse the section and eyeball the first 20 posters. Wrong posters mean
   wrong matches — fix now, not after 500 more files land.
3. `plex_metadata(operation="match")` + `fix_match` for strays, then
   `refresh`.
4. `plex_completeness(operation="scan_library", library_id="…")` for TV —
   catches missing episodes from day one.
5. `plex_canon(operation="afi_100")` or a `check_list` of your 1001-style
   canon — shows what the new shelf still lacks.

## 4. Keeping it clean (monthly, 15 minutes)

- New arrivals: rename → move from `Incoming/` → **Scan**, never the reverse.
- `plex_organization(operation="analyze")` for duplicates and naming drift.
- `plex_completeness` scan for TV gaps; fill or note them.
- `empty_trash` only after confirming the drive was mounted during the scan
  (scanning with a drive offline marks everything missing).
- `optimize_database` quarterly, in a maintenance window.

## 5. Where files may legally come from (orientation, not advice)

Three lawful acquisition paths exist in most jurisdictions: **your own
creations** (phone video, drone footage, DAW exports — always fine),
**licensed downloads and streams** (store purchases, subscription offline
copies — bound by their terms), and **copies of physical media you own**
(the complicated one).

**Ripping a Blu-ray or DVD you bought.** Owning the disc and being allowed
to copy it are different questions, and the answer depends on where you
live — because the blocker is usually not copyright but
**anti-circumvention law**:

- **USA:** the DMCA (§1201) bans circumventing access controls (CSS on DVDs,
  AACS/BD+ on Blu-rays) even for discs you own and even for personal use.
  Ripping tools necessarily circumvent, so personal-use ripping sits in a
  grey zone courts have not resolved in consumers' favor. Format-shifting an
  *unencrypted* disc you own is widely treated as fair use; breaking the
  encryption is the risky step.
- **EU:** the InfoSoc Directive protects "effective technological measures"
  (Art. 6) while allowing member states a private-copying exception
  (Art. 5(2)(b)), usually compensated by levies. States implement this
  differently — some permit private copies only from lawful, non-infringing
  sources.
- **Austria/Germany (§42 UrhG):** private copies for personal use are
  allowed, but *not* by circumventing an effective copy-protection measure,
  and not from an obviously unlawful source. AACS on a Blu-ray counts as
  effective protection.
- **UK:** no broad private-copying exception (the 2014 exception was
  quashed in 2015) — strictly, even personal rips infringe, though
  enforcement against personal use is unheard of.

Practical consequences for a Plex builder: keep receipts and discs (proof of
ownership helps everywhere); never share ripped files outside your household
(uploading/seeding is distribution, unlawful almost everywhere); streaming
your own rips inside your home is the lowest-risk use; and if your country
bans circumvention, the lawful route to digital copies is re-buying digital,
not ripping plastic. None of this is legal advice — laws change, and edge
cases (disability access, preservation, damaged discs) have their own rules.

**Downloads and torrents.** Downloading copyrighted material without
permission infringes in most countries; *uploading* (seeding) is treated
more severely than downloading nearly everywhere, and torrent clients
upload by default while downloading. Ratio rules on private trackers do not
make anything lawful. Lawful torrent uses exist (Linux ISOs, public-domain
and Creative-Commons works, Blizzard-style official distribution) — the
technology is neutral, the content is what counts. Our fleet's
**rtorrent-mcp** (below) is content-agnostic infrastructure; you are
responsible for what you put through it.

## 6. Crossconnect: rtorrent-mcp → plex-mcp (download to shelf)

The fleet's torrent side is **rtorrent-mcp** (backend `10910`, frontend
`10911`): rTorrent over XML-RPC with search, a companion dashboard, and —
critically — a Plex handoff already built in:

1. **Finished downloads get Plex-compliant names automatically.**
   Its filename normalizer writes `Movies/Title (Year)/` and
   `Show/Season NN/SxxEyy` structures — the exact layout section 2 demands.
2. **Plex gets told to scan.** Its media integrator calls back into Plex
   (`PLEX_URL` + `PLEX_TOKEN` in the rtorrent-mcp settings) so new arrivals
   appear without a manual scan and without waiting for a scheduled one.
3. **Flow:** rTorrent → PostProcessor (rename/sort into library folders) →
   MediaIntegrator → Plex section refresh.

Wiring it to *this* server:

1. In rtorrent-mcp settings set `PLEX_URL` (this machine's Plex, usually
   `http://127.0.0.1:32400`) and `PLEX_TOKEN` (same token as here).
2. Point its sorted output at folders your Plex libraries already watch
   (`Movies/`, `TV/`) — or point Plex at its output. One direction only;
   never let both sides "organize" the same tree.
3. After ingest, verify from here: `plex_completeness(operation="scan_library")`
   confirms the episodes actually landed matched, and `plex_canon`
   `check_list` confirms the wanted title arrived as the right match.
4. If rtorrent-mcp reports a section refresh but Plex shows nothing, check
   the usual suspects first: wrong `PLEX_URL` on its side, library watching
   a different folder, or a naming miss (section 2) needing `fix_match`.

*arr users: the same pattern holds — Sonarr/Radarr import into library
folders and notify Plex; rtorrent-mcp is the equivalent for direct (non-*arr)
flows. Run one organizer per tree, not both.
