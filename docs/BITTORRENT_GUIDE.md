# BitTorrent and rtorrent-mcp (protocol, lawful uses, fleet setup)

What BitTorrent technically is, what it is lawful to do with it, how our
fleet's **rtorrent-mcp** fits the Plex pipeline — and where this repo draws
the line on support questions. Companion to
[LIBRARY_BUILDING.md](LIBRARY_BUILDING.md) and
[COLLECTORS_TOOLKIT.md](COLLECTORS_TOOLKIT.md).

> **Not legal advice.** General information for orientation only. And to
> state it once more, plainly: **this repo does not help with copyright
> infringement** — no sources for infringing downloads, no configuration
> help for infringing purposes. See the issue policy at the bottom.

## 1. The protocol in one paragraph

BitTorrent splits files into pieces fetched simultaneously from many peers
while uploading completed pieces to others. It is content-agnostic
infrastructure: efficient, resumable, decentralized distribution with no
central server to pay for. The same mechanism that moves a Linux ISO moves
anything else — the protocol has no opinion, and the law judges the
*content*, never the protocol. Running a client is lawful everywhere;
seeding or downloading copyrighted works without permission generally is
not; and because clients upload while downloading, every torrent download
is also a (small) act of distribution.

## 2. Lawful uses (real, not hypothetical)

- **Free and open-source software distribution.** Linux distributions,
  BSDs, and large datasets ship official torrents. Fast, checksummed,
  and the canonical example of the protocol at its best.
- **Public-domain film.** Early cinema has aged into the public domain
  (in the US, broadly works published before 1929, plus famous one-offs
  like *Night of the Living Dead* (1968), whose copyright was never
  properly secured). The Internet Archive's feature-film collections host
  thousands of such titles lawfully and freely — silent-era classics,
  early noir, ephemeral films. Few compared to a pirate index, but real.
- **Creative-Commons and artist-released works.** The Blender Foundation
  open movies (*Big Buck Bunny*, *Sintel*, *Tears of Steel*), CC-licensed
  music archives, and similar releases are distributed by torrent with the
  creators' blessing.
- **Archival and personal backup.** Moving your *own* large files between
  your own machines (a private tracker with two peers: your NAS and your
  desktop) is just a good transfer protocol.
- **Academic and scientific datasets.** Several projects distribute
  terabyte-scale open datasets by torrent because HTTP hosting would cost
  a fortune.

If your use is on this list, everything below applies to you. If it is
not, nothing below helps you do it — see the issue policy.

## 3. rtorrent-mcp: our fleet torrent side

**rtorrent-mcp** (`D:\Dev\repos\rtorrent-mcp`, backend `10910`, frontend
`10911`) drives **rTorrent** over XML-RPC/SCGI (rTorrent itself is not
bundled; its Docker Compose stack is the recommended way to run one).
What it does:

- Torrent lifecycle: add (magnet/file), monitor, throttle, remove —
  plus search integrations and a companion dashboard.
- **Plex handoff, already built in:** finished downloads are renamed into
  Plex-compliant layouts (`Movies/Title (Year)/`, `Show/Season NN/SxxEyy`)
  by its filename normalizer, then its media integrator triggers a Plex
  section refresh. Configure with `PLEX_URL` + `PLEX_TOKEN` in the
  rtorrent-mcp settings (same values as here).
- Its own web API exposes `/api/plex/status` (is Plex configured?),
  `/api/plex/scan` (trigger a refresh), and `/api/plex/ingest` (manual
  post-processing pass).

The verified pipeline, end to end: rTorrent download → PostProcessor
(rename/sort into library folders) → MediaIntegrator → Plex section
refresh → verify from *this* side with
`plex_completeness(operation="scan_library")` and a
`plex_canon(operation="check_list")` on the wanted title. Full handoff
details: [LIBRARY_BUILDING.md](LIBRARY_BUILDING.md) §6.

**One organizer per tree.** If Sonarr/Radarr manage a folder set, rtorrent
direct flows must not touch the same folders, and vice versa. Two sorters
arguing over filenames is how libraries get duplicated and unmatched.

## 4. Risk notes even for lawful torrenting

- **Swarm visibility.** Your IP is visible to every peer and to anyone
  monitoring the swarm. Copyright trolls monitor popular infringing swarms
  continuously; notices go to the account holder, not necessarily the
  person who clicked. A VPN shifts the visible IP to the provider — which
  merely moves trust, and several "no-log" providers have produced logs.
- **Default upload.** Clients seed while downloading. Ratio requirements,
  seeding to 1.0 "out of politeness," and always-on seeding are all acts
  of distribution with the liability that attaches.
- **Malware.** Executables from untrusted swarms are a classic vector;
  media files far less so, but subtitle and codec-pack lures exist. Scan
  everything, run the client sandboxed or containerized (the Docker setup
  exists partly for this).
- **Japan and strict jurisdictions.** Some countries criminalize even
  personal downloading with real penalties and ISP cooperation —
  Japan most prominently. "Everybody does it" is not a defense there.
  Know the law where *you* sit, not where the guide author sits.

## 5. Issue policy: sourcing questions get declined and closed

So nobody has to improvise in the moment, this is the standing policy for
this repo's issue tracker:

> **Questions asking where to download infringing content — "where do I
> point my torrent app," "best site for X," "which release group," invite
> requests, indexer configuration for infringing purposes — will be
> respectfully declined and the issue closed.** A maintainer replies with a
> short pointer to this document's §2 (lawful uses) and closes. No debate,
> no exceptions, no second chances on the same question. This policy is
> itself documented here so closings never look arbitrary.

Copy-paste close reply: *"Thanks for asking — but this repo doesn't help
with sourcing infringing downloads (see docs/BITTORRENT_GUIDE.md §5).
Lawful uses and the rtorrent-mcp setup are documented there. Closing."*
