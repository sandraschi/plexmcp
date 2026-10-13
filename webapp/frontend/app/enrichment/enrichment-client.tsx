"use client";

import {
	type BulkEnrichmentStatus,
	type EnrichmentStats,
	type EnrichmentThemeHit,
	type LlmProviderInfo,
	type StaleEnrichment,
	getBulkEnrichmentStatus,
	getEnrichmentStats,
	getLlmProviders,
	getStaleEnrichments,
	listLibraries,
	searchByPerson,
	searchByTheme,
	startBulkEnrichment,
} from "@/utils/api";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";

type Library = { id?: string; key?: string; title?: string; type?: string };

function ThemeSearch({ initialTheme }: { initialTheme: string }) {
	const [theme, setTheme] = useState(initialTheme);
	const [hits, setHits] = useState<EnrichmentThemeHit[]>([]);
	const [searching, setSearching] = useState(false);

	const runSearch = async (t: string) => {
		if (!t.trim()) {
			setHits([]);
			return;
		}
		setSearching(true);
		try {
			const res = await searchByTheme(t.trim());
			setHits(res.data);
		} finally {
			setSearching(false);
		}
	};

	useEffect(() => {
		if (initialTheme) void runSearch(initialTheme);
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [initialTheme]);

	return (
		<div className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
			<h2 className="text-sm font-semibold text-slate-200 mb-2">Search by theme</h2>
			<div className="flex gap-2">
				<input
					value={theme}
					onChange={(e) => setTheme(e.target.value)}
					onKeyDown={(e) => e.key === "Enter" && void runSearch(theme)}
					placeholder="e.g. heist, existential, 90s crime"
					className="flex-1 bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm"
				/>
				<button
					type="button"
					onClick={() => void runSearch(theme)}
					disabled={searching}
					className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm hover:bg-slate-600 border border-slate-600/50"
				>
					{searching ? "Searching…" : "Search"}
				</button>
			</div>
			{hits.length > 0 && (
				<div className="flex flex-wrap gap-2 mt-3">
					{hits.map((h) => (
						<Link
							key={h.plex_rating_key}
							href={`/media?ratingKey=${encodeURIComponent(h.plex_rating_key)}`}
							className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600/50 text-sm text-slate-200"
						>
							{h.title}
							{h.year ? ` (${h.year})` : ""}
						</Link>
					))}
				</div>
			)}
		</div>
	);
}

function PersonSearch() {
	const [name, setName] = useState("");
	const [role, setRole] = useState("");
	const [hits, setHits] = useState<EnrichmentThemeHit[]>([]);
	const [searching, setSearching] = useState(false);

	const runSearch = async () => {
		if (!name.trim()) {
			setHits([]);
			return;
		}
		setSearching(true);
		try {
			const res = await searchByPerson(name.trim(), role.trim() || undefined);
			setHits(res.data);
		} finally {
			setSearching(false);
		}
	};

	return (
		<div className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
			<h2 className="text-sm font-semibold text-slate-200 mb-2">Search by person</h2>
			<div className="flex flex-wrap gap-2">
				<input
					value={name}
					onChange={(e) => setName(e.target.value)}
					onKeyDown={(e) => e.key === "Enter" && void runSearch()}
					placeholder="Director or actor name"
					data-testid="person-search-name"
					className="flex-1 min-w-40 bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm"
				/>
				<select
					value={role}
					onChange={(e) => setRole(e.target.value)}
					data-testid="person-search-role"
					className="bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm"
				>
					<option value="">Any role</option>
					<option value="director">Director</option>
					<option value="actor">Actor</option>
				</select>
				<button
					type="button"
					onClick={() => void runSearch()}
					disabled={searching}
					data-testid="person-search-run"
					className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm hover:bg-slate-600 border border-slate-600/50"
				>
					{searching ? "Searching…" : "Search"}
				</button>
			</div>
			{hits.length > 0 && (
				<div data-testid="person-search-results" className="flex flex-wrap gap-2 mt-3">
					{hits.map((h) => (
						<Link
							key={h.plex_rating_key}
							href={`/media?ratingKey=${encodeURIComponent(h.plex_rating_key)}`}
							className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600/50 text-sm text-slate-200"
						>
							{h.title}
							{h.year ? ` (${h.year})` : ""}
						</Link>
					))}
				</div>
			)}
		</div>
	);
}

function EnrichmentPageInner() {
	const searchParams = useSearchParams();
	const initialTheme = searchParams?.get("theme") ?? "";

	const [stats, setStats] = useState<EnrichmentStats | null>(null);
	const [stale, setStale] = useState<StaleEnrichment[]>([]);
	const [libraries, setLibraries] = useState<Library[]>([]);
	const [providers, setProviders] = useState<LlmProviderInfo[]>([]);

	const [libraryId, setLibraryId] = useState("");
	const [maxItems, setMaxItems] = useState(50);
	const [llmProvider, setLlmProvider] = useState("");
	const [llmModel, setLlmModel] = useState("");
	const [starting, setStarting] = useState(false);
	const [job, setJob] = useState<BulkEnrichmentStatus | null>(null);
	const [err, setErr] = useState<string | null>(null);
	const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const refreshStats = async () => {
		try {
			const s = await getEnrichmentStats();
			setStats(s);
		} catch {
			setStats(null);
		}
	};

	useEffect(() => {
		void refreshStats();
		getStaleEnrichments(90)
			.then((r) => setStale(r.data))
			.catch(() => setStale([]));
		listLibraries()
			.then((r) => setLibraries(Array.isArray(r?.data) ? r.data : []))
			.catch(() => setLibraries([]));
		getLlmProviders()
			.then((d) => setProviders(d.providers.filter((p) => p.configured)))
			.catch(() => setProviders([]));
		return () => {
			if (pollRef.current) clearInterval(pollRef.current);
		};
	}, []);

	const startPolling = (jobId: string) => {
		if (pollRef.current) clearInterval(pollRef.current);
		pollRef.current = setInterval(async () => {
			try {
				const status = await getBulkEnrichmentStatus(jobId);
				setJob(status);
				if (status.phase !== "running" && pollRef.current) {
					clearInterval(pollRef.current);
					pollRef.current = null;
					void refreshStats();
				}
			} catch {
				if (pollRef.current) clearInterval(pollRef.current);
				pollRef.current = null;
			}
		}, 2000);
	};

	const handleStart = async () => {
		if (!libraryId) {
			setErr("Pick a library first.");
			return;
		}
		setStarting(true);
		setErr(null);
		try {
			const res = await startBulkEnrichment({
				library_id: libraryId,
				max_items: maxItems,
				llm_provider: llmProvider || undefined,
				llm_model: llmModel || undefined,
			});
			setJob({
				job_id: res.job_id,
				phase: "running",
				total: res.total,
				done: 0,
				failed: 0,
				current_title: "",
				errors: [],
			});
			startPolling(res.job_id);
		} catch (e) {
			setErr(e instanceof Error ? e.message : "Could not start bulk enrichment");
		} finally {
			setStarting(false);
		}
	};

	const eligibleLibraries = libraries.filter((l) => (l.type ?? "").toLowerCase() !== "artist");

	return (
		<div className="max-w-4xl mx-auto p-6 flex flex-col gap-6">
			<div>
				<h1 className="text-3xl font-bold text-slate-100">Deep enrichment</h1>
				<p className="text-slate-400 text-sm mt-1">
					Wikipedia + TMDB + JustWatch, synthesised into a critical dossier per item, with
					cross-references across your library (director, cast, collection, theme).
				</p>
			</div>

			<div className="flex gap-4">
				<div className="flex-1 rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
					<p className="text-xs uppercase tracking-wide text-slate-500">Items enriched</p>
					<p className="text-3xl font-bold text-amber mt-1">{stats?.enriched_count ?? "—"}</p>
				</div>
				<div className="flex-1 rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
					<p className="text-xs uppercase tracking-wide text-slate-500">Stale (&gt;90 days)</p>
					<p className="text-3xl font-bold text-slate-300 mt-1">{stale.length}</p>
				</div>
			</div>

			<div className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4 flex flex-col gap-3">
				<h2 className="text-sm font-semibold text-slate-200">Bulk-enrich a library</h2>
				<div className="flex flex-wrap gap-3 items-end">
					<div>
						<p className="text-xs text-slate-500 mb-1">Library</p>
						<select
							value={libraryId}
							onChange={(e) => setLibraryId(e.target.value)}
							className="bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm min-w-[200px]"
						>
							<option value="">Choose a library…</option>
							{eligibleLibraries.map((l) => (
								<option key={l.key ?? l.id} value={String(l.key ?? l.id)}>
									{l.title} ({l.type})
								</option>
							))}
						</select>
					</div>
					<div>
						<p className="text-xs text-slate-500 mb-1">Max items</p>
						<input
							type="number"
							min={1}
							max={500}
							value={maxItems}
							onChange={(e) => setMaxItems(Number(e.target.value) || 50)}
							className="w-24 bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm"
						/>
					</div>
					<div>
						<p className="text-xs text-slate-500 mb-1">LLM provider (optional)</p>
						<select
							value={llmProvider}
							onChange={(e) => {
								setLlmProvider(e.target.value);
								setLlmModel("");
							}}
							className="bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm"
						>
							<option value="">None (sources only)</option>
							{providers.map((p) => (
								<option key={p.id} value={p.id}>
									{p.label}
								</option>
							))}
						</select>
					</div>
					{llmProvider && (
						<div>
							<p className="text-xs text-slate-500 mb-1">Model</p>
							<input
								value={llmModel}
								onChange={(e) => setLlmModel(e.target.value)}
								placeholder="e.g. gemma3:12b"
								className="bg-slate-800 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-100 text-sm"
							/>
						</div>
					)}
					<button
						type="button"
						disabled={starting || job?.phase === "running"}
						onClick={() => void handleStart()}
						className="px-4 py-2 rounded-lg bg-amber text-slate-900 text-sm font-semibold hover:bg-amber/90 disabled:opacity-60"
					>
						{starting ? "Starting…" : "Start bulk enrichment"}
					</button>
				</div>
				{err && <p className="text-red-400 text-sm">{err}</p>}

				{job && (
					<div className="mt-2">
						<div className="flex justify-between text-xs text-slate-400 mb-1">
							<span>
								{job.done + job.failed} / {job.total}
								{job.current_title ? ` — ${job.current_title}` : ""}
							</span>
							<span>{job.phase}</span>
						</div>
						<div className="h-2 rounded-full bg-slate-800 overflow-hidden">
							<div
								className="h-full bg-amber transition-all"
								style={{ width: `${job.total ? ((job.done + job.failed) / job.total) * 100 : 0}%` }}
							/>
						</div>
						{job.failed > 0 && (
							<p className="text-xs text-red-400 mt-1">{job.failed} item(s) failed.</p>
						)}
					</div>
				)}
			</div>

			<ThemeSearch initialTheme={initialTheme} />
			<PersonSearch />

			{stale.length > 0 && (
				<div className="rounded-lg border border-slate-600/50 bg-slate-900/40 p-4">
					<h2 className="text-sm font-semibold text-slate-200 mb-2">
						Stale dossiers (&gt;90 days old)
					</h2>
					<div className="flex flex-wrap gap-2">
						{stale.slice(0, 30).map((s) => (
							<Link
								key={s.plex_rating_key}
								href={`/media?ratingKey=${encodeURIComponent(s.plex_rating_key)}`}
								className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-600/50 text-sm text-slate-200"
							>
								{s.title}
								{s.year ? ` (${s.year})` : ""}
							</Link>
						))}
					</div>
				</div>
			)}
		</div>
	);
}

export default function EnrichmentPage() {
	return (
		<Suspense fallback={<div className="p-6 text-slate-400">Loading…</div>}>
			<EnrichmentPageInner />
		</Suspense>
	);
}
