# Collector's toolkit (naming, verification, Plex realities, lawful links)

> # ⛔ This guide explicitly does NOT help with copyright infringement.
> **No pirate sites. No release groups to seek out. No sourcing tips, real
> names or wink-wink aliases. Nothing here tells you where to get infringing
> content or how to do it better.** The links below are unambiguously lawful
> resources (metadata databases, edition comparisons, legal availability
> guides, open-source tooling docs). If you came looking for "the big three"
> or similar, you will not find them here — by design, and that will not change.

For builders of large personal libraries: the Scene naming grammar your
files arrive in, how verification works, the honest tension between
Plex-the-company and Plex-the-use-case, how to audit your own shelves with
the tools in this repo, and a link collection of unambiguously lawful
resources. Companion to [LIBRARY_BUILDING.md](LIBRARY_BUILDING.md) (which
covers folder layout, agents, and the ripping-law overview).

> **Not legal advice.** General information for orientation only.

## 1. Scene naming and verification (the grammar, not the sources)

A large share of circulating files carry Scene-style names. Whether your
files arrived lawfully (own rips, store downloads, shared household copies)
or not, the names follow one grammar, and understanding it is what makes
Plex matching work:

```
Show.Name.S01E02.1080p.WEB.H264-GROUP
Movie.Title.1979.2160p.BluRay.REMUX-GROUP
```

Read left to right: **title, season/episode (or year), resolution, source,
codec, releasing group**. For Plex only the first half matters — it reduces
to the `SxxEyy` and `(Year)` conventions from LIBRARY_BUILDING.md §2. The
second half (source/codec/group) is provenance trivia Plex ignores; keep it
in filenames if you like (it helps *you* judge quality), it never hurts
matching.

**Verification files.** `.srr` (Scene ReScene) files store reconstruction
metadata: file lists, checksums, and RAR-store descriptors for a release,
without containing any of the release's content. Their lawful uses are
archival and integrity-checking — verifying that a set of files you already
hold is complete and untampered, or rebuilding damaged archives from
par-data. Tools in the rescene family (`srr`, `pyReScene`) are public
open-source software. Practically: if a multi-part file set fails Plex
import or behaves oddly, checksum verification against available metadata
tells you whether the files are corrupt before you blame the agent, the
scanner, or the disk.

**Quality triage without snobbery.** Resolution numbers lie; bitrate and
source don't. A 4 GB 1080p encode of a 90-minute comedy routinely beats a
25 GB "4K" upscale of the same film on any screen under 65 inches — and for
anything you will watch once, the smaller file wins on every axis (disk,
scan time, transcode load, backup window). Reserve full-disc-size rips for
the dozen films you rewatch yearly. This is storage engineering, not taste:
match the container to the rewatch value.

## 2. Plex-the-company vs Plex-the-use-case (facts, labeled)

**Documented:** Plex-the-company has spent recent years building
ad-supported aggregated streaming (FAST channels, "Discover" integrations,
rentals) into the same client that browses your server. Revenue comes from
ads and partnerships, not from your self-hosted files.

**Widely observed (not company-published):** the self-hosted personal-media
core — people running their own servers for their own files — remains the
product's identity and its most engaged user base, while contributing
little direct revenue. The company markets the free streaming content
heavily; long-time users read that as camouflage, since managing personal
libraries is why nearly everyone in the enthusiast community installed Plex
in the first place.

**Why the tension matters to you:** features for personal libraries
(scanner improvements, agent quality, offline behavior) compete for the
same engineering budget as content partnerships. Plan accordingly —
open metadata agents, local NFO support discussions, and third-party tools
(like this repo) exist precisely because the company's roadmap and the
self-hosters' roadmap are not the same document.

**Monetized shares.** Selling access to a Plex library ("$5/month for 10k
movies") violates Plex's Terms of Service (account termination territory)
and, independently, constitutes commercial-scale distribution of
copyrighted works — the liability category rights-holders actually sue
over, in every jurisdiction in this document. Describing it is not
endorsing it: don't do it, don't buy it, and treat anyone offering it as a
scam risk on top of everything else (shared servers with strangers also
leak your watch history and IP to the operator).

## 3. Audit your own shelves (know what you hold)

Whatever the provenance of your files, you should be able to state what
your library *is*. This repo's tools do that without any external service:

- `plex_reporting(operation="library_stats")` — sizes, types, growth per
  section. Export with `export_report(format="csv")` for a spreadsheet.
- `plex_reporting(operation="content_report")` — codecs, resolutions,
  genres. Finds the 720p stragglers and the mystery files with no metadata.
- `plex_completeness(operation="scan_library")` — missing episodes per
  season. The honest collection audit: what arrived incomplete.
- `plex_canon(operation="check_list", items=[...])` — check your holdings
  against any published list you care about (award winners, a book's film
  appendix, your own top-250).
- `plex_organization(operation="analyze")` — duplicates, naming drift,
  missing matches, empty-trash candidates.

Run the set twice a year. A collector who can export a CSV of 4,000 titles
with codecs and gaps is a librarian; one who can't is a hoarder with a
Plex logo.

## 4. Lawful link collection (the collecting quest, no grey zones)

Every link below is an unambiguously lawful resource. There is no
"wink-wink" section — grey-area directories are deliberately absent.

**Catalog what you own:**

- [Blu-ray.com](https://www.blu-ray.com/) — release database: which editions,
  cuts, and transfers exist. The collector's reference for "which version do
  I actually have."
- [DVDCompare](http://www.dvdcompare.net/) — edition comparisons (cuts,
  extras, aspect ratios) across regions. Essential before re-buying a film.
- [TMDB](https://www.themoviedb.org/) / [TVDB](https://thetvdb.com/) — the
  metadata sources Plex agents read. When a match fails, check how *they*
  spell the title first.
- [MusicBrainz](https://musicbrainz.org/) / [Discogs](https://www.discogs.com/)
  — the same for music, plus a marketplace for buying physical media second-hand.

**Decide what to acquire (lawfully):**

- [JustWatch](https://www.justwatch.com/) — where a title streams, rents, or
  sells in your country right now. The fastest lawful answer to "where do I
  get this."
- Your country's second-hand markets (eBay, local classifieds, charity
  shops) — physical discs are cheap, lawful, and the best source quality
  available to a home user.

**Tools and knowledge (open, lawful software and docs):**

- [MakeMKV forums](https://forum.makemkv.com/) and [Doom9](https://forum.doom9.org/)
  — video-tech knowledge bases (containers, codecs, filters). Tool discussion
  is lawful; what you feed the tools is your responsibility (see §5 of
  LIBRARY_BUILDING.md).
- [VideoHelp](https://www.videohelp.com/) — guides and user reports on
  drives, media, and software behavior.
- Plex's own support articles and forums — agent behavior, scanner quirks,
  naming requirements from the source of truth.

**What is intentionally missing:** torrent indexes, release-group trackers,
DDL forums, "streaming" sites, and invite-market chatter. They are not
documented here — not with real names and not with coy aliases — because a
curated sourcing list for infringing content is exactly what this repo will
not ship. The matching, naming, and auditing knowledge above works
identically on lawfully acquired files.

## 5. Direct answer: may I rip my bought Blu-ray collection?

You asked directly, so here it is plainly — for **Austria** (your
jurisdiction), and again, orientation rather than advice:

**No, not lawfully.** §42 UrhG permits private copies, but expressly
excludes copies made by circumventing an effective technological protection
measure — and Blu-ray AACS/BD+ (like DVD CSS before it) counts as one.
Owning the disc gives you the private-copy exception in principle and
takes it away in practice the moment the ripper breaks the encryption,
which every Blu-ray ripper must. Same result in Germany (§95a UrhG), same
or stricter in the US (DMCA §1201) and UK (no private-copying exception at
all).

Two honest qualifiers, clearly labeled as enforcement reality rather than
law: (a) purely personal, in-home use of self-made rips is essentially
never pursued anywhere — rights-holders chase uploaders, sellers, and
commercial operators; (b) that forbearance can evaporate the moment files
leave the household (shares, seedboxes, "friends" with upload rights).

The lawful routes to digital copies of films you own on plastic remain:
re-buying digital editions, recording from licensed streams where terms
allow, and — for unencrypted discs (home-burned, older non-CSS media) —
ordinary private copying, which the exception genuinely covers. Keep the
discs and receipts regardless: proof of ownership is useful in every
jurisdiction, for every edge case, including damaged-disc replacement
claims.
