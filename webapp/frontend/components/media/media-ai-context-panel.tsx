"use client";

import { type MediaAiContextResponse, getMediaAiContext } from "@/utils/api";
import { safeMediaBlurb } from "@/utils/plex-media-ui";
import { useEffect, useState } from "react";

type Props = {
	ratingKey: string | null;
	onClose: () => void;
};

export function MediaAiContextPanel({ ratingKey, onClose }: Props) {
	const [data, setData] = useState<MediaAiContextResponse | null>(null);
	const [loading, setLoading] = useState(false);
	const [refreshing, setRefreshing] = useState(false);
	const [err, setErr] = useState<string | null>(null);

	useEffect(() => {
		if (!ratingKey) {
			setData(null);
			setErr(null);
			return;
		}
		let cancelled = false;
		setLoading(true);
		setErr(null);
		setData(null);
		getMediaAiContext(ratingKey, false)
			.then((d) => {
				if (!cancelled) setData(d);
			})
			.catch((e: Error) => {
				if (!cancelled) setErr(e.message ?? "Request failed");
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, [ratingKey]);

	useEffect(() => {
		if (!ratingKey) return;
		const h = (e: KeyboardEvent) => {
			if (e.key === "Escape") onClose();
		};
		document.addEventListener("keydown", h);
		return () => document.removeEventListener("keydown", h);
	}, [ratingKey, onClose]);

	const handleRefresh = async () => {
		if (!ratingKey) return;
		setRefreshing(true);
		setErr(null);
		try {
			const d = await getMediaAiContext(ratingKey, true);
			setData(d);
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Refresh failed");
		} finally {
			setRefreshing(false);
		}
	};

	if (!ratingKey) return null;

	const wikiText = safeMediaBlurb(data?.wikipedia?.summary, 8000);
	const llmText = safeMediaBlurb(data?.llm_notes, 8000);
	const tmdbOverview = safeMediaBlurb(data?.tmdb?.overview, 2000);
	const busy = loading || refreshing;

	return (
		<div
			className="fixed inset-0 z-[60] flex items-end sm:items-center justify-center p-4 bg-black/75"
			onClick={onClose}
			role="presentation"
		>
			<div
				className="w-full max-w-lg max-h-[85vh] overflow-hidden rounded-xl glass-panel border border-amber/30 shadow-2xl flex flex-col"
				onClick={(e) => e.stopPropagation()}
				role="dialog"
				aria-modal="true"
				aria-labelledby="ai-context-title"
			>
				<div className="flex items-start justify-between gap-3 p-4 border-b border-slate-600/50">
					<div className="min-w-0">
						<h2 id="ai-context-title" className="text-lg font-bold text-slate-100 truncate">
							AI context
						</h2>
						{data?.plex?.title && (
							<p className="text-sm text-slate-400 truncate">
								{data.plex.title}
								{data.plex.year != null ? ` (${data.plex.year})` : ""}
							</p>
						)}
						{data?.cached === true && !busy && (
							<p className="text-[10px] text-slate-500 mt-0.5">Served from server cache</p>
						)}
					</div>
					<div className="flex shrink-0 gap-2">
						<button
							type="button"
							disabled={busy}
							onClick={() => void handleRefresh()}
							className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-200 text-xs font-medium hover:bg-slate-700 border border-slate-600/50 disabled:opacity-50"
						>
							{refreshing ? "Refreshing…" : "Refresh"}
						</button>
						<button
							type="button"
							onClick={onClose}
							className="px-3 py-1.5 rounded-lg bg-slate-700 text-slate-200 text-sm hover:bg-slate-600 border border-slate-600/50"
						>
							Close
						</button>
					</div>
				</div>

				<div className="p-4 overflow-y-auto flex flex-col gap-4 text-sm">
					{busy && (
						<p className="text-slate-400">
							{refreshing ? "Rebuilding from Wikipedia / TMDB…" : "Loading Wikipedia / TMDB…"}
						</p>
					)}
					{err && <p className="text-red-400 text-sm">{err}</p>}

					{data?.tmdb && (
						<section className="rounded-lg border border-slate-600/50 overflow-hidden bg-slate-900/40">
							<div className="flex gap-3 p-3">
								{data.tmdb.poster_url ? (
									<img
										src={data.tmdb.poster_url}
										alt=""
										className="w-20 shrink-0 rounded object-cover bg-slate-800"
									/>
								) : null}
								<div className="min-w-0 flex-1">
									<p className="text-xs font-semibold uppercase tracking-wide text-amber/90">
										TMDB match
									</p>
									<p className="text-slate-100 font-medium truncate">{data.tmdb.title}</p>
									{data.tmdb.vote_average != null && (
										<p className="text-xs text-slate-400">
											Rating {data.tmdb.vote_average.toFixed(1)} / 10
										</p>
									)}
									{data.tmdb.release_date && (
										<p className="text-xs text-slate-500">{data.tmdb.release_date}</p>
									)}
									<a
										href={data.tmdb.url}
										target="_blank"
										rel="noopener noreferrer"
										className="inline-block mt-2 text-xs font-semibold text-amber hover:underline"
									>
										Open on TMDB
									</a>
								</div>
							</div>
							{tmdbOverview ? (
								<p className="px-3 pb-3 text-slate-300 text-xs leading-relaxed border-t border-slate-600/40 pt-2">
									{tmdbOverview}
								</p>
							) : null}
						</section>
					)}

					{data?.links && (
						<div className="flex flex-wrap gap-2">
							{data.links.wikipedia_article && (
								<a
									href={data.links.wikipedia_article}
									target="_blank"
									rel="noopener noreferrer"
									className="inline-flex px-3 py-2 rounded-lg bg-slate-700 text-slate-100 text-xs font-semibold hover:bg-slate-600 border border-slate-600/50"
								>
									Wikipedia article
								</a>
							)}
							{data.links.wikipedia_search && (
								<a
									href={data.links.wikipedia_search}
									target="_blank"
									rel="noopener noreferrer"
									className="inline-flex px-3 py-2 rounded-lg bg-slate-700 text-slate-100 text-xs font-semibold hover:bg-slate-600 border border-slate-600/50"
								>
									Wikipedia search
								</a>
							)}
							{data.links.tmdb_search && (
								<a
									href={data.links.tmdb_search}
									target="_blank"
									rel="noopener noreferrer"
									className="inline-flex px-3 py-2 rounded-lg bg-slate-700 text-amber/95 text-xs font-semibold hover:bg-slate-600 border border-amber/40"
								>
									TMDB search
								</a>
							)}
						</div>
					)}

					{wikiText && (
						<section>
							<h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">
								Wikipedia
							</h3>
							<p className="text-slate-300 leading-relaxed whitespace-pre-wrap">{wikiText}</p>
						</section>
					)}

					{!busy && data && !wikiText && !data.tmdb && (
						<p className="text-slate-500 text-sm">
							No Wikipedia summary or TMDB match yet. Add a TMDB API key in Settings for posters and
							overviews, or use the search links.
						</p>
					)}

					{llmText && (
						<section>
							<h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1">
								LLM notes
							</h3>
							<p className="text-slate-300 leading-relaxed whitespace-pre-wrap border-l-2 border-amber/50 pl-3">
								{llmText}
							</p>
							<p className="text-[10px] text-slate-500 mt-1">
								Generated from the Wikipedia extract when Ollama / LLM is configured on the backend.
							</p>
						</section>
					)}
				</div>
			</div>
		</div>
	);
}
