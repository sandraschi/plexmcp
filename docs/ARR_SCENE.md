# The *arr Ecosystem

A detailed look at the automation tools commonly used alongside Plex.

---

## What are the *arrs?

The *arr family are open-source tools that automate media library management.
Each tool focuses on a specific media type. They all follow the same design
pattern: you tell them what you want, they find it, download it, and organize
it into your Plex library.

They are **not** part of Plex. They're independent software that you run
alongside Plex on the same machine (or a different one).

---

## The tools

### Core library managers

| Tool | Media | Purpose |
|------|-------|---------|
| **Radarr** | Movies | Monitor wanted movies, search for releases, upgrade quality |
| **Sonarr** | TV Shows | Monitor shows, grab new episodes as they release |
| **Lidarr** | Music | Monitor artists, search for albums/tracks |
| **Readarr** | Ebooks / Audiobooks | Monitor authors, search for books |

### Download clients

| Tool | Protocol | Purpose |
|------|----------|---------|
| **SABnzbd** | Usenet (NZB) | Downloads binary files from Usenet servers |
| **NZBGet** | Usenet (NZB) | Lighter alternative to SABnzbd |
| **qBittorrent** | BitTorrent | Downloads via torrents |
| **Transmission** | BitTorrent | Lightweight torrent client |
| **Deluge** | BitTorrent | Plugin-extensible torrent client |

### Supporting tools

| Tool | Purpose |
|------|---------|
| **Prowlarr** | Indexer manager — connects to torrent/usenet indexer sites, feeds them to all *arrs |
| **Jackett** | Indexer proxy — translates private tracker APIs into a standard format |
| **Bazarr** | Subtitle management — finds subtitles matching your media |
| **Overseerr / Jellyseerr** | Request management — lets users request media, forwards to Radarr/Sonarr |
| **Tautulli** | Plex monitoring — detailed play stats, notifications, graphs |
| **Notifiarr** | Unified notifications from all *arrs and Plex |

---

## How they work together

A typical automated setup:

```
User requests movie (via Overseerr or directly in Radarr)
         ↓
Radarr queries Prowlarr for available releases
         ↓
Prowlarr searches connected indexers (Usenet or Torrent)
         ↓
Radarr picks the best release (quality, size, age)
         ↓
Radarr sends to download client (SABnzbd / qBittorrent)
         ↓
Download client grabs the file
         ↓
Radarr picks up completed download
         ↓
Radarr renames and moves file to Plex library folder
         ↓
Plex detects new file, scans it, metadata appears
```

The entire pipeline runs automatically. Users only interact to make initial
requests or check status.

---

## Why people use them

- **Timeliness**: New episodes appear in Plex within minutes of airing.
- **Quality management**: Automatically upgrade from 720p to 1080p to 4K as
  better releases become available.
- **Curation**: Set rules for preferred release groups, languages, formats.
- **Scale**: Manage libraries of thousands of movies and shows without manual
  effort.

---

## PlexMCP's *arr integration

PlexMCP includes a **read-only** `arr_stack` tool that checks:

- Is Radarr/Sonarr/Lidarr reachable?
- What version are they running?
- How many items are in their download queues?

It does **not** add, remove, or trigger downloads. It's a status check only.
This is intentional — PlexMCP is a Plex tool, not an *arr manager.

The webapp Settings page shows *arr status when the URLs and API keys are
configured in the environment.

---

## Configuration

To use the `arr_stack` tool, set these environment variables:

```bash
RADARR_URL=http://localhost:7878
RADARR_API_KEY=your_radarr_api_key
SONARR_URL=http://localhost:8989
SONARR_API_KEY=your_sonarr_api_key
LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=your_lidarr_api_key
```

API keys are found in each *arr app under **Settings → General → API Key**.

---

## Legal context

The *arr tools are legitimate software. They automate downloads from
indexers you configure. What you download and whether you have the right
to download it depends on:

- **Your local laws** (copyright varies by country)
- **The content's license** (public domain, Creative Commons, your own rips)
- **The source** (private torrents, Usenet, direct downloads)

The *arr tools don't include any content, trackers, or indexers.
Users configure those themselves.

---

## See also

- [PLEX_ECOSYSTEM.md](PLEX_ECOSYSTEM.md) — Plex usage, costs, self-hosted libraries
- [TOOLS.md](TOOLS.md) — PlexMCP tool reference
- [CONFIGURATION.md](CONFIGURATION.md) — environment variables
