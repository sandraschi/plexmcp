# Plex and PlexMCP

A short, user-facing guide to **Plex Media Server** and how this project talks to it.

---

## What is Plex?

**Plex** is a media server you run at home (or on a NAS/VPS). It indexes your movies, TV, music, and photos, fetches artwork and metadata, and serves them to **Plex apps** on TVs, phones, tablets, and the web.

You need:

- **Plex Media Server** installed and running (often at `http://127.0.0.1:32400` on the same machine).
- A **Plex account** (free) to sign in; the server is linked to your account.

PlexMCP does **not** replace Plex — it **connects** to your existing server.

---

## What PlexMCP needs from you

| Item | Why |
|------|-----|
| **X-Plex-Token** | A secret string that proves requests are allowed. PlexMCP sends it on every API call. |
| **Server URL** | Where Plex listens, e.g. `http://127.0.0.1:32400` on the same PC, or `http://192.168.1.10:32400` on your LAN. |

**Getting a token:** Plex’s support article explains it step by step:  
[Finding an authentication token (X-Plex-Token)](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)

Treat the token like a **password**. Do not commit it to git or paste it into public chats.

---

## Remote access (simple mental model)

- **Same machine:** `http://127.0.0.1:32400` is typical.
- **Another device on your home network:** use the server’s LAN IP (e.g. `http://192.168.x.x:32400`). The machine running PlexMCP must be able to **reach** that URL.
- **Away from home:** Plex offers **Remote Access**; URLs can get more complex. Prefer a stable URL Plex shows in **Settings → Remote Access**, or a VPN into your home network so you can still use a LAN-style URL.

If the browser can open Plex but PlexMCP cannot, check firewalls and that `PLEX_URL` matches what actually works in a browser on **that same host**.

---

## What PlexMCP can and cannot do

**Can (via tools / UI):** list libraries, browse media, search, drive optional playback helpers, read server status, optional *arr read-only status, optional RAG over metadata you indexed.

**Cannot:** bypass Plex’s own rules, log in as another user without their token, or edit Plex’s internal database directly like a first-party Plex plugin.

---

## Next steps

- Install PlexMCP: [INSTALL.md](INSTALL.md)  
- Configure env vars: [CONFIGURATION.md](CONFIGURATION.md)  
- Run the web app: [WEBAPP.md](WEBAPP.md)  
- Host safely on a network: [SELF_HOSTING.md](SELF_HOSTING.md)  
