"use client";

import { MediaAiContextPanel } from "@/components/media/media-ai-context-panel";
import { getMediaDetail } from "@/utils/api";
import { playMedia } from "@/utils/playback";
import {
	formatRuntimeMinutes,
	plexImageUrl,
	plexWebDetailsUrl,
	ratingKeyFromItem,
	safeMediaBlurb,
} from "@/utils/plex-media-ui";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const VIEW_KEY = "plex-webapp-movies-view";
type ViewMode = "card" | "list";

interface Lib {
	id?: string | number;
	key?: string;
	title?: string;
	type?: string;
}

interface MoviesClientProps {
	libraries: Lib[];
	items: unknown[];
	selectedLibraryId?: string;
	currentPage: number;
	limit: number;
	hasNext: boolean;
	plexUrl?: string | null;
}

/** Build poster URL via backend image proxy. item.thumb is Plex path e.g. /library/metadata/1/thumb/2 */
function getPosterUrl(item: Record<string, unknown>): string | null {
	const thumb = item?.thumb ?? item?.art;
	if (typeof thumb === "string" && thumb) {
		const path = thumb.replace(/^\//, "");
		return path ? `/api/image/${path}` : null;
	}
	const rk = ratingKeyFromItem(item);
	if (rk) return `/api/image/library/metadata/${rk}/thumb`;
	return null;
}

function MovieItem({
	item,
	index,
	view,
	onClick,
	onAiContext,
}: {
	item: Record<string, unknown>;
	index: number;
	view: ViewMode;
	onClick?: () => void;
	onAiContext?: (item: Record<string, unknown>) => void;
}) {
	const title = String(item?.title ?? item?.name ?? "Unknown");
	const year = item?.year ?? (item as { year?: string })?.year?.toString();
	const summary = safeMediaBlurb(item?.summary ?? item?.plot, 320);
	const key = String(item?.key ?? item?.ratingKey ?? item?.rating_key ?? index);
	const posterUrl = getPosterUrl(item);
	const rk = ratingKeyFromItem(item);

	const cardClass =
		"rounded-xl glass-panel border border-slate-600/50 overflow-hidden hover:border-amber/40 transition-colors cursor-pointer";
	const listClass =
		"flex flex-wrap items-center gap-3 rounded-lg glass-panel border border-slate-600/50 px-4 py-3 hover:border-amber/40 transition-colors cursor-pointer";

	if (view === "list") {
		return (
			<div
				key={key}
				role="button"
				tabIndex={0}
				onClick={onClick}
				onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onClick?.()}
				className={`${listClass} relative`}
			>
				{posterUrl && (
					<img
						src={posterUrl}
						alt=""
						className="w-12 h-12 rounded object-cover shrink-0 bg-slate-800"
					/>
				)}
				<div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 min-w-0 flex-1">
					<p className="font-semibold text-slate-200 shrink-0 min-w-[120px]">{title}</p>
					{year != null && <span className="text-sm text-slate-500">{String(year)}</span>}
					{summary != null && (
						<p className="text-sm text-slate-400 flex-1 min-w-0 line-clamp-1">{summary}</p>
					)}
				</div>
				{onAiContext && rk ? (
					<button
						type="button"
						className="shrink-0 text-xs font-semibold text-amber px-2 py-1 rounded-md border border-amber/40 hover:bg-amber/10"
						onClick={(e) => {
							e.stopPropagation();
							onAiContext(item);
						}}
					>
						AI context
					</button>
				) : null}
			</div>
		);
	}

	return (
		<div
			key={key}
			role="button"
			tabIndex={0}
			onClick={onClick}
			onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onClick?.()}
			className={`${cardClass} relative`}
		>
			{posterUrl ? (
				<img src={posterUrl} alt="" className="w-full aspect-[2/3] object-cover bg-slate-800" />
			) : (
				<div className="w-full aspect-[2/3] bg-slate-800 flex items-center justify-center text-slate-500 text-sm">
					No image
				</div>
			)}
			<div className="p-3">
				<p className="font-semibold text-slate-200 truncate" title={title}>
					{title}
				</p>
				{year != null && <p className="text-sm text-slate-500">{String(year)}</p>}
				{summary != null && <p className="text-xs text-slate-400 mt-1 line-clamp-2">{summary}</p>}
			</div>
			{onAiContext && rk ? (
				<button
					type="button"
					className="absolute bottom-2 right-2 z-10 px-2 py-1 rounded-md text-[11px] font-semibold bg-slate-950/90 text-amber border border-amber/45 hover:bg-slate-900 shadow-md"
					onClick={(e) => {
						e.stopPropagation();
						onAiContext(item);
					}}
				>
					AI context
				</button>
			) : null}
		</div>
	);
}

function MovieModal({
	item,
	plexUrl,
	onClose,
	onOpenAiContext,
}: {
	item: Record<string, unknown>;
	plexUrl?: string | null;
	onClose: () => void;
	/** Open lazy Wikipedia / TMDB / LLM panel (same as card “AI context”). */
	onOpenAiContext?: () => void;
}) {
	const [detail, setDetail] = useState<Record<string, unknown> | null>(null);
	const [detailLoading, setDetailLoading] = useState(false);
	const [detailError, setDetailError] = useState<string | null>(null);
	const [playBusy, setPlayBusy] = useState(false);
	const [playErr, setPlayErr] = useState<string | null>(null);

	const display = useMemo(() => ({ ...item, ...(detail ?? {}) }), [item, detail]);
	const ratingKey = ratingKeyFromItem(display);

	const title = String(display?.title ?? display?.name ?? "Unknown");
	const year = display?.year ?? (display as { year?: string })?.year?.toString();
	const summary = safeMediaBlurb(display?.summary ?? display?.plot, 12_000);
	const posterUrl =
		plexImageUrl(display?.thumb as string | undefined) ??
		plexImageUrl(display?.art as string | undefined) ??
		getPosterUrl(display as Record<string, unknown>);
	const contentRating = display?.content_rating ?? display?.contentRating;
	const rating = display?.rating ?? display?.audience_rating;
	const duration = display?.duration;
	const genres = (display?.genres as string[] | undefined) ?? [];
	const directors = (display?.directors as string[] | undefined) ?? [];
	const writers = (display?.writers as string[] | undefined) ?? [];
	const studio = display?.studio;
	const tagline = display?.tagline;
	const collections = (display?.collections as string[] | undefined) ?? [];
	const actors = (display?.actors as { name?: string; role?: string }[] | undefined) ?? [];
	const mediaInfo = (display?.media_info as Record<string, unknown>[] | undefined) ?? [];
	const viewCount = display?.view_count;

	const plexWebUrl = ratingKey ? plexWebDetailsUrl(plexUrl ?? null, ratingKey) : null;
	const durationStr = formatRuntimeMinutes(duration != null ? Number(duration) : null);

	useEffect(() => {
		const rk = ratingKeyFromItem(item);
		if (!rk) {
			setDetail(null);
			setDetailError(null);
			setDetailLoading(false);
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
	}, [item]);

	useEffect(() => {
		const h = (e: KeyboardEvent) => {
			if (e.key === "Escape") onClose();
		};
		document.addEventListener("keydown", h);
		return () => document.removeEventListener("keydown", h);
	}, [onClose]);

	const handlePlayClient = async () => {
		if (!ratingKey) return;
		setPlayBusy(true);
		setPlayErr(null);
		try {
			await playMedia(ratingKey);
		} catch (e) {
			setPlayErr(e instanceof Error ? e.message : "Playback failed");
		} finally {
			setPlayBusy(false);
		}
	};

	const mi0 = mediaInfo[0];

	return (
		<div
			className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70"
			onClick={onClose}
			role="dialog"
			aria-modal="true"
			aria-labelledby="movie-modal-title"
		>
			<div
				className="rounded-xl glass-panel border border-slate-600/50 max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-xl"
				onClick={(e) => e.stopPropagation()}
			>
				<div className="flex flex-1 min-h-0">
					{/* Poster: fixed width, 2:3 aspect */}
					<div className="w-48 sm:w-56 shrink-0 aspect-[2/3] bg-slate-900/50 overflow-hidden">
						{posterUrl ? (
							<img src={posterUrl} alt="" className="w-full h-full object-cover" />
						) : (
							<div className="w-full h-full flex items-center justify-center text-slate-500 text-sm">
								No image
							</div>
						)}
					</div>

					{/* Content: scrollable */}
					<div className="flex-1 min-w-0 overflow-y-auto flex flex-col">
						<div className="p-6">
							<h2 id="movie-modal-title" className="text-2xl font-bold text-slate-100 pr-8">
								{title}
							</h2>
							<div className="flex flex-wrap gap-x-3 gap-y-1 mt-2 text-sm text-slate-400">
								{year != null && <span>{String(year)}</span>}
								{durationStr && <span>{durationStr}</span>}
								{contentRating != null && <span>{String(contentRating)}</span>}
								{rating != null && <span>{Number(rating).toFixed(1)}</span>}
								{studio != null ? <span>{String(studio)}</span> : null}
							</div>
							{tagline != null ? (
								<p className="text-amber/90 italic text-sm mt-3">{String(tagline)}</p>
							) : null}
							{genres.length > 0 && (
								<div className="flex flex-wrap gap-2 mt-3">
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
								<p className="text-slate-400 text-sm mt-2">
									Director{directors.length > 1 ? "s" : ""}: {directors.join(", ")}
								</p>
							)}
							{summary != null ? (
								<p className="text-slate-300 text-sm mt-4 leading-relaxed">{summary}</p>
							) : null}

							{detailLoading && (
								<p className="text-slate-500 text-xs mt-3">Loading full metadata…</p>
							)}
							{detailError && <p className="text-amber/80 text-xs mt-3">{detailError}</p>}

							{writers.length > 0 && (
								<p className="text-slate-400 text-sm mt-3">Writers: {writers.join(", ")}</p>
							)}
							{actors.length > 0 && (
								<div className="mt-3">
									<p className="text-slate-500 text-xs font-semibold uppercase tracking-wide mb-1">
										Cast
									</p>
									<ul className="text-sm text-slate-400 space-y-0.5 max-h-32 overflow-y-auto">
										{actors.slice(0, 12).map((a, i) => (
											<li key={`${a.name ?? "a"}-${i}`}>
												<span className="text-slate-300">{a.name}</span>
												{a.role ? <span className="text-slate-500"> — {a.role}</span> : null}
											</li>
										))}
									</ul>
								</div>
							)}
							{collections.length > 0 && (
								<p className="text-slate-400 text-sm mt-3">Collections: {collections.join(", ")}</p>
							)}
							{viewCount != null && Number(viewCount) > 0 && (
								<p className="text-slate-500 text-xs mt-2">Plays: {String(viewCount)}</p>
							)}
							{mi0 && (
								<p className="text-slate-500 text-xs mt-3 font-mono">
									{[mi0.video_resolution, mi0.video_codec, mi0.audio_codec, mi0.container]
										.filter(Boolean)
										.join(" · ")}
								</p>
							)}
						</div>

						<div className="mt-auto p-6 pt-0 flex flex-wrap items-center gap-3 border-t border-slate-600/50">
							{ratingKey && (
								<button
									type="button"
									disabled={playBusy}
									onClick={() => void handlePlayClient()}
									className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber text-slate-900 font-semibold hover:bg-amber/90 transition-colors disabled:opacity-60"
								>
									{playBusy ? "Starting…" : "Play on client"}
								</button>
							)}
							{plexWebUrl && (
								<a
									href={plexWebUrl}
									target="_blank"
									rel="noopener noreferrer"
									className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-700 text-slate-100 font-semibold hover:bg-slate-600 border border-slate-600/50 transition-colors"
								>
									Open in Plex Web
								</a>
							)}
							{ratingKey && onOpenAiContext ? (
								<button
									type="button"
									onClick={onOpenAiContext}
									className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-purple-400/50 text-purple-200 font-semibold hover:bg-purple-950/40 transition-colors"
								>
									AI context
								</button>
							) : null}
							{playErr && <span className="text-red-400 text-sm w-full">{playErr}</span>}
							<button
								type="button"
								onClick={onClose}
								className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 hover:bg-slate-600 border border-slate-600/50"
							>
								Close
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}

export function MoviesClient({
	libraries,
	items,
	selectedLibraryId,
	currentPage,
	limit,
	hasNext,
	plexUrl,
}: MoviesClientProps) {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [viewMode, setViewMode] = useState<ViewMode>("card");
	const [selectedMovie, setSelectedMovie] = useState<Record<string, unknown> | null>(null);
	const [aiContextRatingKey, setAiContextRatingKey] = useState<string | null>(null);

	const openAiContext = (row: Record<string, unknown>) => {
		const rk = ratingKeyFromItem(row);
		if (rk) setAiContextRatingKey(rk);
	};

	useEffect(() => {
		const stored = localStorage.getItem(VIEW_KEY);
		if (stored === "list" || stored === "card") setViewMode(stored);
	}, []);

	const updateView = (v: ViewMode) => {
		setViewMode(v);
		if (typeof window !== "undefined") localStorage.setItem(VIEW_KEY, v);
	};

	const setPage = (page: number) => {
		const next = new URLSearchParams(searchParams?.toString() ?? "");
		next.set("page", String(page));
		if (limit !== 24) next.set("limit", String(limit));
		router.push(`/movies?${next.toString()}`);
	};

	const handleLibraryChange = (libraryId: string) => {
		const next = new URLSearchParams(searchParams?.toString() ?? "");
		if (libraryId) next.set("library_id", libraryId);
		else next.delete("library_id");
		next.delete("page");
		router.push(`/movies?${next.toString()}`);
	};

	return (
		<>
			<MediaAiContextPanel
				ratingKey={aiContextRatingKey}
				onClose={() => setAiContextRatingKey(null)}
			/>
			{selectedMovie && (
				<MovieModal
					item={selectedMovie}
					plexUrl={plexUrl}
					onClose={() => setSelectedMovie(null)}
					onOpenAiContext={() => openAiContext(selectedMovie)}
				/>
			)}
			<div className="mb-6 flex flex-wrap items-center gap-4">
				{libraries.length > 0 && (
					<div className="flex items-center gap-2">
						<label className="text-sm text-slate-400">Library:</label>
						<select
							value={selectedLibraryId ?? ""}
							onChange={(e) => handleLibraryChange(e.target.value)}
							className="px-3 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm min-w-[180px]"
						>
							<option value="">All movie libraries</option>
							{libraries.map((lib) => (
								<option
									key={String(lib.id ?? lib.key ?? lib.title)}
									value={String(lib.id ?? lib.key ?? "")}
								>
									{lib.title ?? lib.key ?? "Library"}
								</option>
							))}
						</select>
					</div>
				)}
				<div className="flex items-center gap-2 ml-auto">
					<span className="text-sm text-slate-400">View:</span>
					<button
						type="button"
						onClick={() => updateView("card")}
						className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
							viewMode === "card"
								? "bg-amber/20 border-amber/50 text-amber"
								: "glass-panel border-slate-600/50 text-slate-400 hover:text-slate-200"
						}`}
					>
						Cards
					</button>
					<button
						type="button"
						onClick={() => updateView("list")}
						className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
							viewMode === "list"
								? "bg-amber/20 border-amber/50 text-amber"
								: "glass-panel border-slate-600/50 text-slate-400 hover:text-slate-200"
						}`}
					>
						List
					</button>
				</div>
			</div>

			{viewMode === "card" ? (
				<div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
					{items.map((item, i) => {
						const row = item as Record<string, unknown>;
						const key = String(row?.key ?? row?.ratingKey ?? i);
						return (
							<MovieItem
								key={key}
								item={row}
								index={i}
								view="card"
								onClick={() => setSelectedMovie(row)}
								onAiContext={openAiContext}
							/>
						);
					})}
				</div>
			) : (
				<div className="flex flex-col gap-2">
					{items.map((item, i) => {
						const row = item as Record<string, unknown>;
						const key = String(row?.key ?? row?.ratingKey ?? i);
						return (
							<MovieItem
								key={key}
								item={row}
								index={i}
								view="list"
								onClick={() => setSelectedMovie(row)}
								onAiContext={openAiContext}
							/>
						);
					})}
				</div>
			)}

			{items.length === 0 && <p className="text-slate-500 py-8">No movies found.</p>}

			{(currentPage > 1 || hasNext) && items.length > 0 && (
				<div className="mt-8 flex flex-wrap items-center justify-center gap-4">
					<button
						type="button"
						onClick={() => setPage(currentPage - 1)}
						disabled={currentPage <= 1}
						className="px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber/40"
					>
						Previous
					</button>
					<span className="text-sm text-slate-400">
						Page {currentPage}
						{hasNext ? " (more available)" : ""}
					</span>
					<button
						type="button"
						onClick={() => setPage(currentPage + 1)}
						disabled={!hasNext}
						className="px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber/40"
					>
						Next
					</button>
				</div>
			)}
		</>
	);
}
