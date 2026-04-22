"use client";

import { getMediaDetail } from "@/utils/api";
import { playMedia } from "@/utils/playback";
import {
	formatRuntimeMinutes,
	plexImageUrl,
	plexWebDetailsUrl,
	ratingKeyFromItem,
	safeMediaBlurb,
} from "@/utils/plex-media-ui";
import { PlayIcon, XMarkIcon } from "@heroicons/react/24/solid";
import React, { useEffect, useMemo, useState } from "react";

interface MovieMetadataModalProps {
	movie: Record<string, unknown> | null;
	onClose: () => void;
	/** Base Plex URL from settings (for “Open in Plex Web”). */
	plexUrl?: string | null;
	/** Open Wikipedia / TMDB / LLM context panel. */
	onOpenAiContext?: () => void;
}

export default function MovieMetadataModal({
	movie,
	onClose,
	plexUrl,
	onOpenAiContext,
}: MovieMetadataModalProps) {
	const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
	const [detailLoading, setDetailLoading] = useState(false);
	const [detailError, setDetailError] = useState<string | null>(null);
	const [isPlaying, setIsPlaying] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const display = useMemo(() => {
		if (!movie) return null;
		return { ...movie, ...(detail ?? {}) };
	}, [movie, detail]);

	const ratingKey = display ? ratingKeyFromItem(display) : null;

	useEffect(() => {
		if (!movie) return;
		const rk = ratingKeyFromItem(movie);
		if (!rk) {
			setDetail(null);
			setDetailError(null);
			return;
		}
		let cancelled = false;
		setDetailLoading(true);
		setDetailError(null);
		setDetail(null);
		getMediaDetail(rk)
			.then((res) => {
				if (!cancelled && res.data && typeof res.data === "object") {
					setDetail(res.data as Record<string, unknown>);
				}
			})
			.catch((e: Error) => {
				if (!cancelled) setDetailError(e.message ?? "Could not load details");
			})
			.finally(() => {
				if (!cancelled) setDetailLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, [movie]);

	useEffect(() => {
		const h = (e: KeyboardEvent) => {
			if (e.key === "Escape") onClose();
		};
		document.addEventListener("keydown", h);
		return () => document.removeEventListener("keydown", h);
	}, [onClose]);

	if (!movie || !display) return null;

	const title = String(display.title ?? display.name ?? "Unknown");
	const year = display.year != null ? String(display.year) : null;
	const summary = safeMediaBlurb(display.summary ?? display.plot, 12_000);
	const tagline = safeMediaBlurb(display.tagline, 400);
	const type = display.type != null ? String(display.type) : null;

	const backdropUrl =
		plexImageUrl(display.art as string | undefined) ??
		plexImageUrl(display.thumb as string | undefined);
	const posterUrl = plexImageUrl(display.thumb as string | undefined);

	const genres = (display.genres as string[] | undefined) ?? [];
	const directors = (display.directors as string[] | undefined) ?? [];
	const writers = (display.writers as string[] | undefined) ?? [];
	const studio = display.studio != null ? String(display.studio) : null;
	const contentRating = display.content_rating != null ? String(display.content_rating) : null;
	const rating = display.rating;
	const durationStr = formatRuntimeMinutes(
		display.duration != null ? Number(display.duration) : null,
	);
	const actors = (display.actors as { name?: string; role?: string }[] | undefined) ?? [];
	const collections = (display.collections as string[] | undefined) ?? [];
	const mediaInfo = (display.media_info as Record<string, unknown>[] | undefined) ?? [];
	const mi0 = mediaInfo[0];
	const plexWebUrl = ratingKey ? plexWebDetailsUrl(plexUrl ?? null, ratingKey) : null;

	const handlePlay = async () => {
		if (!ratingKey) return;
		setIsPlaying(true);
		setError(null);
		try {
			await playMedia(ratingKey);
		} catch (err: unknown) {
			setError(err instanceof Error ? err.message : "Failed to start playback");
		} finally {
			setIsPlaying(false);
		}
	};

	return (
		<div
			className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
			onClick={onClose}
			role="presentation"
		>
			<div
				className="relative w-full max-w-4xl overflow-hidden rounded-2xl bg-slate-900 shadow-2xl ring-1 ring-white/10"
				onClick={(e) => e.stopPropagation()}
				role="dialog"
				aria-modal="true"
				aria-labelledby="movie-metadata-title"
			>
				{backdropUrl && (
					<div className="absolute inset-0 h-64 opacity-20">
						<img src={backdropUrl} alt="" className="h-full w-full object-cover" />
						<div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-900" />
					</div>
				)}

				<button
					type="button"
					onClick={onClose}
					title="Close"
					aria-label="Close"
					className="absolute top-4 right-4 z-10 rounded-full bg-black/50 p-2 text-white hover:bg-white/20 transition-colors"
				>
					<XMarkIcon className="h-6 w-6" />
				</button>

				<div className="relative z-0 flex flex-col md:flex-row gap-6 p-6 md:p-8 mt-4">
					<div className="flex-shrink-0 w-32 md:w-64 mx-auto md:mx-0">
						{posterUrl ? (
							<img src={posterUrl} alt="" className="w-full rounded-lg shadow-xl" />
						) : (
							<div className="w-full aspect-[2/3] bg-slate-800 rounded-lg flex items-center justify-center text-slate-500">
								No Poster
							</div>
						)}
					</div>

					<div className="flex-1 flex flex-col gap-4 text-slate-100 min-w-0">
						<div>
							<h2 id="movie-metadata-title" className="text-3xl font-bold">
								{title}
							</h2>
							<div className="flex flex-wrap items-center gap-3 text-sm text-slate-400 mt-1">
								{year && <span>{year}</span>}
								{durationStr && <span>{durationStr}</span>}
								{contentRating && <span>{contentRating}</span>}
								{rating != null && Number.isFinite(Number(rating)) && (
									<span>{Number(rating).toFixed(1)} ★</span>
								)}
								{studio && <span>{studio}</span>}
								{type && (
									<span className="uppercase text-xs font-bold bg-slate-800 px-2 py-0.5 rounded">
										{type}
									</span>
								)}
							</div>
						</div>

						{tagline && (
							<p className="text-lg italic text-slate-300 font-light">&ldquo;{tagline}&rdquo;</p>
						)}

						{genres.length > 0 && (
							<div className="flex flex-wrap gap-2">
								{genres.map((g) => (
									<span
										key={g}
										className="px-2 py-0.5 rounded bg-slate-700/80 text-slate-300 text-xs"
									>
										{g}
									</span>
								))}
							</div>
						)}

						{directors.length > 0 && (
							<p className="text-slate-400 text-sm">
								Director{directors.length > 1 ? "s" : ""}: {directors.join(", ")}
							</p>
						)}
						{writers.length > 0 && (
							<p className="text-slate-400 text-sm">Writers: {writers.join(", ")}</p>
						)}

						<div className="prose prose-invert max-w-none text-sm">
							<p>{summary ?? "No summary available."}</p>
						</div>

						{detailLoading && <p className="text-slate-500 text-xs">Loading full metadata…</p>}
						{detailError && <p className="text-amber/80 text-xs">{detailError}</p>}

						{actors.length > 0 && (
							<div>
								<p className="text-slate-500 text-xs font-semibold uppercase tracking-wide mb-1">
									Cast
								</p>
								<ul className="text-sm text-slate-400 space-y-0.5 max-h-28 overflow-y-auto">
									{actors.slice(0, 14).map((a, i) => (
										<li key={`${a.name ?? "a"}-${i}`}>
											<span className="text-slate-300">{a.name}</span>
											{a.role ? <span className="text-slate-500"> — {a.role}</span> : null}
										</li>
									))}
								</ul>
							</div>
						)}

						{collections.length > 0 && (
							<p className="text-slate-400 text-sm">Collections: {collections.join(", ")}</p>
						)}

						{mi0 && (
							<p className="text-slate-500 text-xs font-mono">
								{[mi0.video_resolution, mi0.video_codec, mi0.audio_codec, mi0.container]
									.filter(Boolean)
									.join(" · ")}
							</p>
						)}

						<div className="mt-auto pt-6 flex flex-col gap-2">
							{error && (
								<div className="text-red-400 text-sm bg-red-900/20 p-2 rounded">{error}</div>
							)}
							<div className="flex flex-wrap gap-3">
								{ratingKey && (
									<button
										type="button"
										onClick={() => void handlePlay()}
										disabled={isPlaying}
										className={`flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-lg transition-all ${
											isPlaying
												? "bg-amber-600 cursor-wait opacity-80 text-black"
												: "bg-amber-500 hover:bg-amber-400 hover:scale-[1.02] active:scale-[0.98] text-black shadow-lg shadow-amber-500/20"
										}`}
									>
										<PlayIcon className="h-6 w-6" />
										{isPlaying ? "Starting…" : "Play on client"}
									</button>
								)}
								{plexWebUrl && (
									<a
										href={plexWebUrl}
										target="_blank"
										rel="noopener noreferrer"
										className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold bg-slate-700 text-slate-100 hover:bg-slate-600 border border-slate-600/50"
									>
										Open in Plex Web
									</a>
								)}
								{ratingKey && onOpenAiContext ? (
									<button
										type="button"
										onClick={onOpenAiContext}
										className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold border border-purple-400/50 text-purple-200 hover:bg-purple-950/40"
									>
										AI context
									</button>
								) : null}
							</div>
							<p className="text-xs text-center text-slate-500">
								Play on client uses the active Plex app (or first available client).
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
