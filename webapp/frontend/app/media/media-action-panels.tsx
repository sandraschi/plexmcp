"use client";

import {
	type PlaybackClient,
	getMediaArt,
	getMediaFile,
	getMediaStreamUrl,
	listPlaybackClients,
	playMedia,
} from "@/utils/api";
import { useEffect, useState } from "react";

export function MediaFilesPanel({ ratingKey }: { ratingKey: string }) {
	const [stream, setStream] = useState<string | null>(null);
	const [file, setFile] = useState<string | null>(null);
	const [art, setArt] = useState<{ cover?: string | null; poster?: string | null } | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		let cancelled = false;
		(async () => {
			setLoading(true);
			try {
				const [s, f, a] = await Promise.all([
					getMediaStreamUrl(ratingKey).catch(() => null),
					getMediaFile(ratingKey).catch(() => null),
					getMediaArt(ratingKey).catch(() => null),
				]);
				if (cancelled) return;
				setStream((s?.url ?? s?.urls?.[0] ?? null) as string | null);
				setFile((f?.file ?? null) as string | null);
				setArt(a ? { cover: a.cover_url, poster: a.poster_url ?? a.artwork_url } : null);
			} catch (e) {
				if (!cancelled) setError(e instanceof Error ? e.message : "Could not load file info");
			} finally {
				if (!cancelled) setLoading(false);
			}
		})();
		return () => {
			cancelled = true;
		};
	}, [ratingKey]);

	return (
		<section
			aria-label="Files and artwork"
			data-testid="media-files"
			className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4"
		>
			<h2 className="text-xs font-semibold uppercase tracking-wide text-amber/90 mb-2">
				Files and artwork
			</h2>
			{loading ? (
				<p className="text-sm text-slate-500">Loading file info…</p>
			) : error ? (
				<p className="text-sm text-red-400">{error}</p>
			) : (
				<div className="flex flex-col gap-2 text-sm">
					<p className="text-slate-300 break-all">
						Local file: <span className="text-slate-500">{file ?? "not available"}</span>
					</p>
					<p className="text-slate-300 break-all">
						Stream URL:{" "}
						{stream ? (
							<a
								href={stream}
								target="_blank"
								rel="noopener noreferrer"
								className="text-amber hover:underline"
							>
								open stream
							</a>
						) : (
							<span className="text-slate-500">not available</span>
						)}
					</p>
					{(art?.cover || art?.poster) && (
						<div className="flex gap-3 mt-1">
							{art.cover && (
								<img src={art.cover} alt="" className="w-24 rounded object-cover bg-slate-800" />
							)}
							{art.poster && art.poster !== art.cover && (
								<img src={art.poster} alt="" className="w-24 rounded object-cover bg-slate-800" />
							)}
						</div>
					)}
				</div>
			)}
		</section>
	);
}

export function MediaPlaybackPanel({
	ratingKey,
	mediaKey,
}: { ratingKey: string; mediaKey?: string }) {
	const [clients, setClients] = useState<PlaybackClient[]>([]);
	const [clientId, setClientId] = useState("");
	const [msg, setMsg] = useState<string | null>(null);
	const [busy, setBusy] = useState(false);

	useEffect(() => {
		let cancelled = false;
		listPlaybackClients()
			.then((res) => {
				if (cancelled) return;
				const list = (res.data ?? res.clients ?? []) as PlaybackClient[];
				setClients(list);
				const first = list[0];
				const id = first ? String(first.id ?? first.name ?? "") : "";
				if (id) setClientId(id);
			})
			.catch(() => {});
		return () => {
			cancelled = true;
		};
	}, []);

	const play = async () => {
		setBusy(true);
		setMsg(null);
		try {
			await playMedia(mediaKey ?? ratingKey, clientId || undefined);
			setMsg("Play command sent (best-effort — client support varies).");
		} catch (e) {
			setMsg(e instanceof Error ? e.message : "Play failed");
		} finally {
			setBusy(false);
		}
	};

	return (
		<section
			aria-label="Playback"
			data-testid="media-playback"
			className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4"
		>
			<h2 className="text-xs font-semibold uppercase tracking-wide text-amber/90 mb-2">Playback</h2>
			<div className="flex flex-wrap items-center gap-2">
				<select
					value={clientId}
					onChange={(e) => setClientId(e.target.value)}
					data-testid="playback-client"
					className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-600/50 text-slate-100 text-sm min-w-40"
				>
					{clients.length === 0 && <option value="">No clients found</option>}
					{clients.map((c, i) => {
						const id = String(c.id ?? c.name ?? i);
						return (
							<option key={id} value={id}>
								{String(c.title ?? c.name ?? id)}
							</option>
						);
					})}
				</select>
				<button
					type="button"
					onClick={() => void play()}
					disabled={busy}
					data-testid="playback-play"
					className="px-4 py-1.5 rounded-lg bg-amber text-slate-950 text-sm font-semibold hover:bg-amber/90 disabled:opacity-60"
				>
					{busy ? "Sending…" : "Play on client"}
				</button>
			</div>
			{msg && <p className="text-xs text-slate-400 mt-2">{msg}</p>}
			<p className="text-[10px] text-slate-500 mt-1">
				Best-effort: Plex client support varies (see PRD known gaps).
			</p>
		</section>
	);
}
