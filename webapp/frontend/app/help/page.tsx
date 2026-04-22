"use client";

import clsx from "clsx";
import { ArrowLeft, BookOpen, Cpu, Globe, Layers, Monitor, Server } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

type Section = "mcp" | "webapp" | "plex" | "ecosystem" | "arr";

const sections: { id: Section; label: string; icon: typeof Cpu }[] = [
	{ id: "mcp", label: "Plex MCP server", icon: Cpu },
	{ id: "webapp", label: "Web dashboard", icon: Monitor },
	{ id: "plex", label: "Plex Media Server", icon: Server },
	{ id: "ecosystem", label: "Plex ecosystem", icon: Globe },
	{ id: "arr", label: "*arr ecosystem", icon: Layers },
];

function sectionClass() {
	return "space-y-4 text-slate-300 text-sm leading-relaxed [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:text-slate-100 [&_h2]:mt-8 [&_h2]:first:mt-0 [&_h3]:text-base [&_h3]:font-medium [&_h3]:text-slate-200 [&_h3]:mt-6 [&_ul]:list-disc [&_ul]:pl-5 [&_ul]:space-y-2 [&_ol]:list-decimal [&_ol]:pl-5 [&_ol]:space-y-2 [&_code]:text-amber [&_code]:text-xs [&_code]:bg-slate-800/80 [&_code]:px-1 [&_code]:py-0.5 [&_code]:rounded [&_strong]:text-amber";
}

function McpSection() {
	return (
		<article className={sectionClass()}>
			<h2>What is Plex MCP?</h2>
			<p>
				<strong>PlexMCP</strong> is a Model Context Protocol server that exposes your Plex Media
				Server to AI assistants (Cursor, Claude, VS Code, etc.). Tools are grouped into{" "}
				<em>portmanteau</em> tools (e.g. <code className="text-amber">plex_library</code>,{" "}
				<code className="text-amber">plex_server</code>,{" "}
				<code className="text-amber">plex_search</code>) so agents get one clear interface per
				domain instead of dozens of micro-tools.
			</p>

			<h3>Transports</h3>
			<ul>
				<li>
					<strong>stdio</strong> — default for local MCP clients; the client launches the Python
					process.
				</li>
				<li>
					<strong>HTTP / SSE</strong> — optional; useful when the MCP host connects over the
					network. Ports and env vars are documented in the repo README and central-docs fleet
					standards.
				</li>
			</ul>

			<h3>Authentication</h3>
			<p>
				The server reads <code>PLEX_TOKEN</code> and <code>PLEX_URL</code> (or{" "}
				<code>PLEX_SERVER_URL</code>) from the environment. The token is the same{" "}
				<em>X-Plex-Token</em> you use in Plex Web; never commit it to git.
			</p>

			<h3>Key tools (examples)</h3>
			<ul>
				<li>
					<code>plex_server</code> — status, info, health, maintenance-related operations.
				</li>
				<li>
					<code>plex_library</code> — list/get libraries, scan, refresh, metadata paths.
				</li>
				<li>
					<code>plex_media</code> / <code>plex_search</code> — browse and search your libraries.
				</li>
				<li>
					<code>plex_streaming</code> — sessions, clients, playback control (where supported by
					Plex).
				</li>
				<li>
					Optional RAG / semantic features depend on backend indexing and embedding configuration
					(see README).
				</li>
				<li>
					<code>arr_stack</code> — optional read-only Radarr/Sonarr/Lidarr HTTP snapshot when URLs
					and API keys are set (same data as the Overview card).
				</li>
			</ul>

			<h3>Sampling &amp; agentic flows</h3>
			<p>
				FastMCP 3.x features (sampling, skills) may be enabled for multi-step workflows. If your
				client does not support sampling, the server can fall back to a local OpenAI-compatible
				endpoint (e.g. Ollama) when configured.
			</p>
		</article>
	);
}

function WebappSection() {
	return (
		<article className={sectionClass()}>
			<h2>Web dashboard</h2>
			<p>
				This UI is a <strong>Next.js</strong> front end talking to a <strong>FastAPI</strong>{" "}
				backend. The backend does not reimplement Plex logic—it calls PlexMCP tools in-process (same
				Python package as the MCP server) so behavior matches the MCP tools.
			</p>

			<h3>Default ports (fleet)</h3>
			<ul>
				<li>
					<strong>Backend API</strong> — <code>http://127.0.0.1:10740</code> (REST, OpenAPI at{" "}
					<code>/docs</code>).
				</li>
				<li>
					<strong>Frontend</strong> — <code>http://127.0.0.1:10741</code> (this app).
				</li>
			</ul>
			<p>
				Ports are chosen to sit in the 10700+ range (fleet registry). Adjust only if you have a
				conflict.
			</p>

			<h3>Startup</h3>
			<p>
				From the repo <code>webapp</code> folder, use the provided <code>start.ps1</code> (clears
				ports, builds, runs). Set environment variables in <code>webapp/backend/.env</code> (at
				minimum <code>PLEX_TOKEN</code> and Plex URL).
			</p>

			<h3>Pages</h3>
			<ul>
				<li>
					<strong>Overview</strong> — quick connection check, shortcuts, and optional *arr status
					(if configured in Settings).
				</li>
				<li>
					<strong>Libraries / Movies / Search</strong> — browse and search your media through the
					API.
				</li>
				<li>
					<strong>Semantic search</strong> — optional; requires RAG index and embeddings.
				</li>
				<li>
					<strong>Chat</strong> — LLM chat with context; configure provider and base URL in backend
					settings.
				</li>
				<li>
					<strong>Server</strong> — Plex server info (overview + raw JSON).
				</li>
				<li>
					<strong>Settings</strong> — token and LLM-related settings where exposed.
				</li>
			</ul>

			<h3>Top bar</h3>
			<p>
				Quick links to other fleet webapps, container UIs, a short <strong>Help</strong> modal, and{" "}
				<strong>Logs</strong> (tail of the backend log file). Use this page for full documentation.
			</p>
		</article>
	);
}

function PlexSection() {
	return (
		<article className={sectionClass()}>
			<h2>Plex Media Server</h2>
			<p>
				PlexMCP talks to your Plex server over HTTP using the official API patterns (via Python
				libraries). The server must be reachable from the machine running PlexMCP (same host, LAN,
				or Tailscale/VPN—your network rules apply).
			</p>

			<h3>Finding your token</h3>
			<ol>
				<li>Open Plex Web in your browser (signed in).</li>
				<li>
					<strong>Settings</strong> → <strong>Account</strong> → <strong>Authorized devices</strong>{" "}
					(or use an XML request with a logged-in session—see Plex support articles).
				</li>
				<li>
					Copy the <strong>X-Plex-Token</strong> and set it as <code>PLEX_TOKEN</code>.
				</li>
			</ol>
			<p>
				Official reference:{" "}
				<a
					href="https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/"
					className="text-amber hover:underline"
					target="_blank"
					rel="noopener noreferrer"
				>
					Finding an authentication token
				</a>
				.
			</p>

			<h3>Server URL</h3>
			<p>
				For a local Plex install, <code>http://127.0.0.1:32400</code> or{" "}
				<code>http://localhost:32400</code> is typical. For remote access, use the URL that works in
				your browser (HTTPS, custom port, or Tailscale IP).
			</p>

			<h3>Libraries &amp; agents</h3>
			<p>
				Libraries appear in the <strong>Server</strong> page after a successful connection. If
				something is missing, confirm in Plex that libraries are scanned, and that your token has
				access to that server.
			</p>

			<h3>Transcoding &amp; playback</h3>
			<p>
				Playback and session control depend on Plex clients and API capabilities. Some operations
				are placeholders or limited by what Plex exposes; check tool responses for{" "}
				<code>NOT_IMPLEMENTED</code> or error messages.
			</p>

			<h3>Troubleshooting</h3>
			<ul>
				<li>
					<strong>401 / unauthorized</strong> — token wrong or revoked; regenerate in Plex.
				</li>
				<li>
					<strong>Connection refused</strong> — Plex not running, wrong URL, or firewall blocking
					port 32400.
				</li>
				<li>
					<strong>Empty libraries</strong> — scan libraries in Plex; confirm you are querying the
					correct server.
				</li>
			</ul>
		</article>
	);
}

function EcosystemSection() {
	return (
		<article className={sectionClass()}>
			<h2>Plex ecosystem</h2>
			<p>
				Plex is both a <strong>company</strong> (Plex Inc.) and a <strong>product family</strong>:
				server software, apps on almost every platform, optional subscriptions, and ad-supported
				streaming. This tab is context for how Plex fits together—not official Plex documentation.
			</p>

			<h3>Plex Media Server and clients</h3>
			<p>
				<strong>Plex Media Server (PMS)</strong> runs on a PC, NAS, or appliance; it indexes your
				libraries, fetches metadata, and streams to clients. <strong>Clients</strong> include web,
				mobile (iOS/Android), TV platforms (Android TV, Apple TV, Roku, etc.), desktop apps, and
				game consoles. Playback can be direct or transcoded depending on format, client, and
				network.
			</p>

			<h3>Plexamp</h3>
			<p>
				<strong>Plexamp</strong> is Plex&apos;s focused <strong>music</strong> player (desktop and
				mobile). It connects to the same server, supports high-quality playback, playlists, offline
				downloads (where offered), and features like Sonic recommendations on eligible libraries. It
				is separate from the main Plex video apps.
			</p>

			<h3>The company</h3>
			<p>
				<strong>Plex Inc.</strong> evolved from a media-center hobby project into a commercial
				product company. Revenue comes from <strong>Plex Pass</strong> (subscription perks: hardware
				transcoding, downloads, music features, etc.), optional add-ons, and{" "}
				<strong>ad-supported</strong> streaming catalogs. The business model is separate from your
				personal library—you can run Plex for private media without using their paid VOD catalogs.
			</p>

			<h3>Free and ad-supported content</h3>
			<p>
				Besides hosting your own files, Plex offers <strong>free, ad-supported</strong> movies and
				shows (availability varies by region), podcasts, and discovery features inside the apps.
				That catalog is unrelated to files on your disk; your libraries remain under your control.
			</p>

			<h3>Private media libraries (typical use)</h3>
			<p>
				The classic reason people run Plex is a <strong>private library</strong>: rips of discs you
				own, phone videos, drone footage, DAW exports, lecture recordings, Creative Commons /
				public-domain media, and other files you store on a NAS or home server. Plex provides the
				library UI, metadata, and streaming—<strong>you</strong> remain responsible for the{" "}
				<strong>legality</strong> of what you store and share.
			</p>

			<h3>Sources often discussed online (copyright)</h3>
			<p>
				Community forums often <em>name</em> third-party sites when talking about where files
				originate. PlexMCP does not source media and does not endorse any particular site. In many
				jurisdictions, downloading or sharing copyrighted material without permission is unlawful.
				Only add content you have the <strong>right</strong> to use (e.g. your own creations,
				properly licensed material, or public-domain works).
			</p>
			<ul>
				<li>
					<strong>YTS</strong> — A long-running name associated with <strong>movie torrent</strong>{" "}
					releases in forum culture; often cited in threads about file names and quality tiers. Not
					affiliated with Plex.
				</li>
				<li>
					<strong>Nyaa</strong> — A <strong>torrent index</strong> strongly associated with{" "}
					<strong>anime</strong> and East Asian releases; community uploads vary widely in legality
					and quality.
				</li>
				<li>
					<strong>PB (The Pirate Bay)</strong> — A well-known <strong>torrent indexer</strong> that
					appears often in generic &quot;where do files come from&quot; discussions; high legal risk
					for copyrighted works in most countries.
				</li>
			</ul>
			<p className="text-slate-500 border border-slate-600/50 rounded-lg px-3 py-2 bg-slate-900/40">
				<strong className="text-slate-400">Practical note:</strong> Plex scans folders you point at
				on disk. If you acquire files from any source, organize them in a way that matches
				Plex&apos;s naming conventions, keep your server updated, and respect your local laws and
				the rights of creators.
			</p>
		</article>
	);
}

function ArrSection() {
	return (
		<article className={sectionClass()}>
			<h2>The *arr ecosystem</h2>
			<p>
				The <strong>*arr</strong> family (sometimes written <strong>arr stack</strong> or{" "}
				<strong>*arr suite</strong>) is a set of open-source apps for <strong>organizing</strong>{" "}
				and <strong>automating</strong> media libraries. They share similar web UIs and conventions.
				They are <strong>not</strong> made by Plex Inc., but many people run them{" "}
				<strong>alongside</strong> Plex: the *arr apps download or import files into folders that
				Plex then libraries and streams.
			</p>

			<h3>Docker and media stacks</h3>
			<p>
				Most people run these apps in <strong>Docker</strong> (or Podman) as part of a{" "}
				<strong>media stack</strong>: Radarr, Sonarr, Lidarr, Prowlarr, download clients, and
				sometimes Plex on the same host or VLAN. Compose files publish standard ports (e.g. 7878 /
				8989 / 8686) or a <strong>reverse proxy</strong> (Traefik, Nginx, Caddy) exposes them under
				hostnames like <code className="text-amber">https://radarr.home</code>.
			</p>
			<p>
				For PlexMCP&apos;s optional integration, enter the{" "}
				<strong>same base URL you use in a browser</strong> to open each app, from the{" "}
				<strong>machine running the webapp backend</strong> (same Docker host → often{" "}
				<code className="text-amber">http://127.0.0.1:PORT</code>; another server or Tailscale → use
				that host or internal DNS). API keys come from each app under Settings → General → Security.
			</p>

			<h3>Common apps (examples)</h3>
			<ul>
				<li>
					<strong>Radarr</strong> — Movies: monitored titles, quality profiles, upgrades, disk
					naming.
				</li>
				<li>
					<strong>Sonarr</strong> — TV series: seasons/episodes, calendar, missing-episode search.
				</li>
				<li>
					<strong>Lidarr</strong> — Music: artists/albums, similar workflow to Sonarr/Radarr.
				</li>
				<li>
					<strong>Readarr</strong> — E-books and audiobooks.
				</li>
				<li>
					<strong>Prowlarr</strong> — <strong>Indexer manager</strong>: one place to configure
					indexers and sync them to your *arr apps (and many torrent/usenet clients) via API.
				</li>
				<li>
					<strong>Bazarr</strong> — Subtitles: fetches SRT/ASS for content *arr already organized
					(often paired with Sonarr/Radarr).
				</li>
				<li>Others (Whisparr, etc.) follow the same pattern for other media types.</li>
			</ul>

			<h3>Typical flow with Plex</h3>
			<ol>
				<li>*arr downloads or moves media into a folder structure you define.</li>
				<li>
					Plex <strong>library paths</strong> point at those folders (or parent folders). Plex scans
					and matches metadata.
				</li>
				<li>
					You watch in Plex clients; *arr keeps the library &quot;filled&quot; or upgraded according
					to your rules.
				</li>
			</ol>

			<h3>Download clients and indexers</h3>
			<p>
				*arr apps usually talk to <strong>download clients</strong> (e.g. SABnzbd, qBittorrent,
				Deluge) and get release lists from <strong>indexers</strong> (often managed through
				Prowlarr). Setup is separate from Plex: you configure networks, paths, and credentials in
				each app.
			</p>

			<h3>PlexMCP and *arr (optional)</h3>
			<p>
				This webapp can store <strong>Radarr</strong>, <strong>Sonarr</strong>, and{" "}
				<strong>Lidarr</strong> base URLs and <strong>API keys</strong> in Settings (written to{" "}
				<code className="text-amber">data/settings.json</code> on the backend). The backend then
				probes each app over HTTP (read-only): version, reachability, and{" "}
				<strong>queue counts</strong>. The Overview page shows a short summary; the MCP tool{" "}
				<code className="text-amber">arr_stack(operation=&quot;status&quot;)</code> returns the same
				snapshot for AI agents.
			</p>
			<p>
				This is <strong>not</strong> full *arr automation (no searches, no downloads, no Prowlarr).
				For that, use each app&apos;s UI or a dedicated MCP server if you add one later.
			</p>

			<h3>Legal and practical note</h3>
			<p>
				*arr tools are often used for <strong>automation</strong> of acquisition. You are
				responsible for complying with copyright, your ISP&apos;s terms, and local law. Many users
				only automate content they have the right to obtain (e.g. Usenet subscriptions, legal
				torrents, or files they already own).
			</p>
		</article>
	);
}

export default function HelpPage() {
	const [section, setSection] = useState<Section>("mcp");

	return (
		<div className="container mx-auto p-6 max-w-4xl">
			<div className="flex items-center gap-4 mb-6">
				<Link
					href="/"
					className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-amber transition-colors"
				>
					<ArrowLeft className="w-4 h-4" />
					Back to overview
				</Link>
			</div>

			<div className="flex items-start gap-3 mb-2">
				<BookOpen className="w-7 h-7 text-amber shrink-0 mt-0.5" />
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Help &amp; documentation</h1>
					<p className="text-slate-500 mt-1 text-sm">
						PlexMCP, this dashboard, Plex, and related ecosystems (including *arr) — in one place.
					</p>
				</div>
			</div>

			<div className="mt-8 flex flex-wrap gap-1 border-b border-slate-600/50 pb-px">
				{sections.map(({ id, label, icon: Icon }) => (
					<button
						key={id}
						type="button"
						onClick={() => setSection(id)}
						className={clsx(
							"flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors border border-b-0 -mb-px",
							section === id
								? "bg-slate-800/90 text-amber border-slate-600/60"
								: "bg-transparent text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/40",
						)}
					>
						<Icon className="w-4 h-4 shrink-0" />
						{label}
					</button>
				))}
			</div>

			<div className="mt-6 glass-panel-strong rounded-xl p-6 md:p-8 border border-slate-600/50">
				{section === "mcp" && <McpSection />}
				{section === "webapp" && <WebappSection />}
				{section === "plex" && <PlexSection />}
				{section === "ecosystem" && <EcosystemSection />}
				{section === "arr" && <ArrSection />}
			</div>

			<p className="text-slate-600 text-xs mt-8 text-center">
				For API details, open the backend{" "}
				<a
					href="http://127.0.0.1:10740/docs"
					className="text-amber/80 hover:underline"
					target="_blank"
					rel="noreferrer"
				>
					OpenAPI docs
				</a>{" "}
				when the backend is running.
			</p>
		</div>
	);
}
