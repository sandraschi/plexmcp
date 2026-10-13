"use client";

import { MediaAiContextPanel } from "@/components/media/media-ai-context-panel";
import {
	type EnrichmentReport,
	type LlmProviderInfo,
	type RelatedMediaItem,
	enrichMedia,
	getEnrichment,
	getLlmProviders,
	getRelatedMedia,
} from "@/utils/api";
import Link from "next/link";
import { useEffect, useState } from "react";
import { MediaFilesPanel, MediaPlaybackPanel } from "./media-action-panels";

const SOURCE_OPTIONS = [
	{ id: "wikipedia", label: "Wikipedia" },
	{ id: "tmdb", label: "TMDB (deep)" },
	{ id: "justwatch", label: "JustWatch (availability)" },
];

const RELATION_LABELS: Record<string, string> = {
	director: "By the same director",
	shared_cast: "Shares cast",
	same_collection: "Same collection",
	thematic: "Thematically related",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
	if (!children || (typeof children === "string" && !children.trim())) return null;
	return (
		<section className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
			<h2 className="text-xs font-semibold uppercase tracking-wide text-amber/90 mb-2">{title}</h2>
			<div className="text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">{children}</div>
		</section>
	);
}

export function MediaDetailClient({ ratingKey }: { ratingKey: string }) {
	const [report, setReport] = useState<EnrichmentReport | null>(null);
	const [related, setRelated] = useState<RelatedMediaItem[]>([]);
	const [loading, setLoading] = useState(true);
	const [enriching, setEnriching] = useState(false);
	const [err, setErr] = useState<string | null>(null);
	const [providers, setProviders] = useState<LlmProviderInfo[]>([]);
	const [llmProvider, setLlmProvider] = useState("");
	const [llmModel, setLlmModel] = useState("");
	const [sources, setSources] = useState<string[]>(["wikipedia", "tmdb", "justwatch"]);
	const [showOptions, setShowOptions] = useState(false);
	const [aiContextKey, setAiContextKey] = useState<string | null>(null);

	const load = async () => {
		setLoading(true);
		setErr(null);
		try {
			const [existing, rel] = await Promise.all([
				getEnrichment(ratingKey),
				getRelatedMedia(ratingKey).catch(() => ({ success: true, data: [], count: 0 })),
			]);
			setReport(existing.data);
			setRelated(rel.data);
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Failed to load");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		void load();
		getLlmProviders()
			.then((d) => setProviders(d.providers.filter((p) => p.configured)))
			.catch(() => setProviders([]));
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [ratingKey]);

	const handleEnrich = async (forceRefresh: boolean) => {
		setEnriching(true);
		setErr(null);
		try {
			const result = await enrichMedia(ratingKey, {
				force_refresh: forceRefresh,
				sources,
				llm_provider: llmProvider || undefined,
				llm_model: llmModel || undefined,
			});
			setReport(result);
			const rel = await getRelatedMedia(ratingKey).catch(() => ({
				data: [] as RelatedMediaItem[],
			}));
			setRelated(rel.data);
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Enrichment failed");
		} finally {
			setEnriching(false);
		}
	};

	const toggleSource = (id: string) => {
		setSources((prev) => (prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]));
	};

	const sections = report?.report_sections;
	const tmdbRaw = (report?.raw_data?.tmdb ?? null) as { poster_url?: string } | null;
	const grouped = related.reduce<Record<string, RelatedMediaItem[]>>((acc, r) => {
		if (!acc[r.relation_type]) acc[r.relation_type] = [];
		acc[r.relation_type].push(r);
		return acc;
	}, {});

	return (
		<div className="max-w-5xl mx-auto p-6 flex flex-col gap-6">
			<div className="flex flex-wrap items-start justify-between gap-4">
				<div>
					<h1 className="text-3xl font-bold text-slate-100">
						{report?.title ?? "Media dossier"}
						{report?.year ? (
							<span className="text-slate-500 font-normal"> ({report.year})</span>
						) : null}
					</h1>
					<p className="text-slate-500 text-sm mt-1">
						Deep enrichment dossier &middot; rating key {ratingKey}
					</p>
				</div>
				<div className="flex gap-2">
					<button
						type="button"
						onClick={() => setAiContextKey(ratingKey)}
						data-testid="media-ai-context-open"
						className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm font-medium hover:bg-slate-600 border border-slate-600/50"
					>
						AI context
					</button>
					<button
						type="button"
						onClick={() => setShowOptions((v) => !v)}
						className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm font-medium hover:bg-slate-600 border border-slate-600/50"
					>
						{showOptions ? "Hide options" : "Options"}
					</button>
					<button
						type="button"
						disabled={enriching}
						onClick={() => void handleEnrich(!!report)}
						className="px-4 py-2 rounded-lg bg-amber text-slate-900 text-sm font-semibold hover:bg-amber/90 disabled:opacity-60"
					>
						{enriching ? "Enriching…" : report ? "Re-enrich" : "Enrich now"}
					</button>
				</div>
			</div>

			{showOptions && (
				<div className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4 flex flex-col gap-3 text-sm">
					<div>
						<p className="text-slate-400 mb-1.5">Sources</p>
						<div className="flex flex-wrap gap-3">
							{SOURCE_OPTIONS.map((s) => (
								<label key={s.id} className="flex items-center gap-1.5 text-slate-300">
									<input
										type="checkbox"
										checked={sources.includes(s.id)}
										onChange={() => toggleSource(s.id)}
									/>
									{s.label}
								</label>
							))}
						</div>
					</div>
					<div className="flex flex-wrap gap-3">
						<div>
							<p className="text-slate-400 mb-1.5">
								LLM provider (optional - synthesises the dossier)
							</p>
							<select
								value={llmProvider}
								onChange={(e) => {
									setLlmProvider(e.target.value);
									setLlmModel("");
								}}
								className="bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-1.5 text-slate-100"
							>
								<option value="">None (sources only, no dossier synthesis)</option>
								{providers.map((p) => (
									<option key={p.id} value={p.id}>
										{p.label}
									</option>
								))}
							</select>
						</div>
						{llmProvider && (
							<div>
								<p className="text-slate-400 mb-1.5">Model</p>
								<input
									value={llmModel}
									onChange={(e) => setLlmModel(e.target.value)}
									placeholder="e.g. gemma3:12b"
									className="bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-1.5 text-slate-100"
								/>
							</div>
						)}
					</div>
				</div>
			)}

			{err && <p className="text-red-400 text-sm">{err}</p>}
			{loading && <p className="text-slate-400">Loading…</p>}

			{!loading && !report && !err && (
				<div className="rounded-lg border border-amber/30 bg-amber/5 p-6 text-center">
					<p className="text-slate-300">No dossier yet for this item.</p>
					<p className="text-slate-500 text-sm mt-1">
						Click "Enrich now" above to fetch Wikipedia/TMDB/JustWatch and (optionally) synthesise a
						critical dossier.
					</p>
				</div>
			)}

			{report && (
				<div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-6">
					{tmdbRaw?.poster_url ? (
						<img
							src={tmdbRaw.poster_url}
							alt=""
							className="w-full rounded-lg object-cover bg-slate-800 self-start"
						/>
					) : null}
					<div className="flex flex-col gap-4">
						<Section title="Synopsis">{sections?.synopsis}</Section>
						<Section title="Why this matters">{sections?.why_this_matters}</Section>
						<Section title="Critical overview">{sections?.critical_overview}</Section>
						<Section title="Production notes">{sections?.production_notes}</Section>
						<Section title="Reception at release">{sections?.reception_at_release}</Section>
						<Section title="Legacy">{sections?.legacy}</Section>
						<Section title="Director context">{sections?.director_context}</Section>
						<Section title="Key cast notes">{sections?.key_cast_notes}</Section>

						{sections?.content_warnings &&
						Object.values(sections.content_warnings).some((v) =>
							Array.isArray(v) ? v.length : v,
						) ? (
							<section className="rounded-lg border border-red-500/30 bg-red-950/20 p-4">
								<h2 className="text-xs font-semibold uppercase tracking-wide text-red-300 mb-2">
									Content warnings
								</h2>
								<ul className="text-slate-300 text-sm space-y-1">
									{sections.content_warnings.violence && (
										<li>
											<strong>Violence:</strong> {sections.content_warnings.violence}
										</li>
									)}
									{sections.content_warnings.sexual_content && (
										<li>
											<strong>Sexual content:</strong> {sections.content_warnings.sexual_content}
										</li>
									)}
									{sections.content_warnings.language && (
										<li>
											<strong>Language:</strong> {sections.content_warnings.language}
										</li>
									)}
									{(sections.content_warnings.other_triggers ?? []).map((t) => (
										<li key={t}>{t}</li>
									))}
								</ul>
							</section>
						) : null}

						{sections?.thematic_tags && sections.thematic_tags.length > 0 && (
							<div className="flex flex-wrap gap-2">
								{sections.thematic_tags.map((t) => (
									<Link
										key={t}
										href={`/enrichment?theme=${encodeURIComponent(t)}`}
										className="px-3 py-1 rounded-full bg-slate-700 text-slate-200 text-xs hover:bg-slate-600 border border-slate-600/50"
									>
										{t}
									</Link>
								))}
							</div>
						)}

						{sections?.awards && sections.awards.length > 0 && (
							<Section title="Awards">
								<ul className="list-disc list-inside">
									{sections.awards.map((a) => (
										<li key={a}>{a}</li>
									))}
								</ul>
							</Section>
						)}
						{sections?.trivia && sections.trivia.length > 0 && (
							<Section title="Trivia">
								<ul className="list-disc list-inside">
									{sections.trivia.map((t) => (
										<li key={t}>{t}</li>
									))}
								</ul>
							</Section>
						)}

						<p className="text-[10px] text-slate-500">
							Sources fetched: {report.sources_fetched.join(", ") || "none"}
							{report.sources_failed.length > 0 && (
								<> &middot; unavailable: {report.sources_failed.join(", ")}</>
							)}
						</p>
					</div>
				</div>
			)}

			<MediaFilesPanel ratingKey={ratingKey} />
			<MediaPlaybackPanel ratingKey={ratingKey} />
			<MediaAiContextPanel ratingKey={aiContextKey} onClose={() => setAiContextKey(null)} />

			{Object.keys(grouped).length > 0 && (
				<div className="flex flex-col gap-4">
					<h2 className="text-lg font-semibold text-slate-200">Related in your library</h2>
					{Object.entries(grouped).map(([relType, items]) => (
						<div key={relType}>
							<p className="text-xs uppercase tracking-wide text-slate-500 mb-2">
								{RELATION_LABELS[relType] ?? relType}
							</p>
							<div className="flex flex-wrap gap-2">
								{items.map((r) => (
									<Link
										key={`${r.target_rating_key}-${r.relation_detail}`}
										href={`/media?ratingKey=${encodeURIComponent(r.target_rating_key)}`}
										className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600/50 text-sm text-slate-200"
									>
										{r.target_title ?? r.target_rating_key}
										{r.target_year ? ` (${r.target_year})` : ""}
									</Link>
								))}
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
