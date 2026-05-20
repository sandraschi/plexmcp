# The Plex Ecosystem

A plain-language guide to Plex, how people use it, what it costs, and the tools
and communities around it.

---

## What is Plex?

**Plex Media Server** is software you run on your own computer, NAS, or server.
It indexes your media files (movies, TV shows, music, photos), fetches artwork
and metadata (posters, summaries, ratings), and streams them to any device:
smart TVs, phones, tablets, game consoles, web browsers.

You manage your own library. Plex just organizes and serves it.

There are two parts:

- **Plex Media Server** — the software that runs on your machine, scans your
  files, and streams them.
- **Plex Apps** — the client software on your TV, phone, etc. that connects to
  your server.

The server is free. The apps are free to install. Some features require a
**Plex Pass** subscription.

---

## Plex Pass: what costs money

Plex is free to use for the basics. A **Plex Pass** ($5/month or $120 lifetime)
adds:

| Feature | Free | Plex Pass |
|---------|------|-----------|
| Stream your media to any device | Yes | Yes |
| Organize your media library | Yes | Yes |
| Mobile app playback (phone/tablet) | 1-min limit | Unlimited |
| Hardware-accelerated transcoding | No | Yes |
| Intro/credit detection (auto-skip) | No | Yes |
| Trailers & extras | No | Yes |
| Lyrics for music | No | Yes |
| Offline downloads (mobile) | No | Yes |
| Plexamp (dedicated music player) | Basic | Full |

Some users run happily on free forever. Others buy the lifetime Pass for
hardware transcoding (helps when streaming to slow devices) or the mobile
unlock.

---

## Self-hosted libraries vs Plex-provided content

This is the key distinction in the Plex world:

### Your own media library (self-hosted)

You point Plex at folders full of your own files:

```
/media/Movies/
/media/TV Shows/
/media/Music/
```

Plex scans these folders, matches each file against online databases (TMDB,
TVDB, MusicBrainz), and downloads posters, summaries, ratings, cast info.
This is what PlexMCP interacts with.

You provide the files. Plex provides the shelf.

### Plex-provided content

Plex also offers streaming content that you didn't add yourself:

- **Plex Movies & TV** — ad-supported free movies and shows (like a mini
  streaming service). US-only mostly.
- **Plex Live TV** — free ad-supported live channels (news, sports, etc.).
- **Plex News** — aggregated news clips.
- **Plexamp Radio** — algorithmic music stations.

This content comes from Plex's servers, not your hard drive. It has ads
(unless you have Plex Pass). It's unrelated to your personal library.

**Important:** Self-hosted libraries are the core use case for PlexMCP. The
tools browse, search, and manage YOUR media, not Plex's ad-supported content.

---

## How people get media for self-hosted libraries

Since Plex organizes your files but doesn't supply them, users need to get
media from somewhere. The most common sources:

- **Your own rips** — DVDs, Blu-rays, CDs you own, ripped to digital files.
- **Digital purchases** — movies bought on iTunes, Amazon, etc., downloaded
  and added to Plex.
- **Recordings** — over-the-air TV recordings via Plex's DVR feature (with a
  compatible TV tuner).
- **Acquisition** — many users acquire media from the internet. This is where
  the conversation gets nuanced.

The practical reality is that a large portion of the self-hosted media
community uses content obtained from sources that may not be licensed for that
use. This is not unique to Plex — it's the same dynamic as CDs being ripped,
DVDs being backed up, or streaming downloads being saved locally.

We don't moralize about this. PlexMCP is a tool for managing and interacting
with a Plex server. What files you put in your libraries is your business.

---

## The *arr stack (automated library management)

The *arr family of tools automates finding, downloading, organizing, and
upgrading media. They're commonly run alongside Plex:

| Tool | Purpose |
|------|---------|
| **Radarr** | Movie library management — finds wanted movies, upgrades quality |
| **Sonarr** | TV show library management — monitors shows, grabs new episodes |
| **Lidarr** | Music library management |
| **Readarr** | Ebook and audiobook management |
| **SABnzbd** | Usenet download client (used by *arrs to grab files) |
| **qBittorrent / Transmission** | BitTorrent clients (alternative to Usenet) |
| **Prowlarr** | Indexer manager — feeds search sources to Radarr/Sonarr/etc. |
| **Bazarr** | Subtitle management — finds and downloads subtitles |

These tools work together:

1. You add a movie to Radarr.
2. Radarr searches for it (via Prowlarr-connected indexers).
3. Radarr sends it to SABnzbd or qBittorrent.
4. The download client grabs the file.
5. Radarr picks it up, renames it, moves it to your Plex library folder.
6. Plex scans the folder and the media appears.

PlexMCP includes a read‑only `arr_stack` tool that checks whether Radarr,
Sonarr, and Lidarr are reachable and how many items are in their queues.
It does **not** trigger downloads or manage the *arr apps.

---

## Common setup patterns

### Minimal (Plex only)

```
[Media files] → [Plex Media Server] → [Plex Apps (TV, phone, etc.)]
```

### Automated (Plex + *arrs)

```
[Usenet/Torrent] → [SABnzbd/qBittorrent] → [Radarr/Sonarr] → [Plex]
                                                           → [PlexMCP]
```

### With PlexMCP

```
[Plex Media Server] ← [PlexMCP] ← [Claude Desktop / Cursor / other MCP clients]
                                           ↓
                                    [Webapp] (optional browser UI)
```

---

## A note on terminology

- **Plex** is the company and the product name.
- **Plex Media Server** is the server software (sometimes just "PMS").
- **Plex Pass** is the paid subscription tier.
- **\*arr** (pronounced "star-arr") refers collectively to Radarr, Sonarr, etc.
- **Metadata** is the posters, summaries, ratings, cast info that Plex fetches.
- **Transcoding** means converting a video on-the-fly to a format the playback
  device can handle (e.g., converting 4K HDR to 1080p SDR for a phone).

---

## Next steps

- [INSTALL.md](INSTALL.md) — set up PlexMCP
- [QUICKSTART.md](QUICKSTART.md) — get running in \~60 seconds
- [WEBAPP.md](WEBAPP.md) — start the browser UI
- [ARR_SCENE.md](ARR_SCENE.md) — more detail on the *arr ecosystem
- [TOOLS.md](TOOLS.md) — MCP tool reference
