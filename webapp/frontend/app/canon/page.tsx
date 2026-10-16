"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import {
	type CanonEntry,
	type CanonResult,
	canonAfi,
	canonCheckList,
	canonOscars,
	canonTmdb,
} from "@/utils/api";
import { BACKEND_DOWN_HINT } from "@/utils/config-hints";
import { Award, Clapperboard, Search } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

type CanonId = "oscars" | "afi" | "tmdb" | "paste";

const TABS: { id: CanonId; label: string; hint: string }[] = [
	{ id: "oscars", label: "Oscar winners", hint: "Every Best Picture winner, live list" },
	{ id: "afi", label: "AFI 100", hint: "AFI 2007 top-100, live list" },
	{ id: "tmdb", label: "TMDB top", hint: "Top-rated movies + TV (needs TMDB key)" },
	{ id: "paste", label: "Paste a list", hint: "Your own canon, e.g. 1001-style slice" },
];

const LIMITS = [10, 25, 50];

function entrySub(e: CanonEntry): string {
	const bits: string[] = [];
	if (e.rank != null) bits.push(`#${e.rank}`);
	if (e.year != null) bits.push(String(e.year));
	if (e.held_as?.title) bits.push(`held as "${e.held_as.title}"`);
	if (e.reason) bits.push(e.reason);
	return bits.join(" · ");
}

function MissingTable({ rows }: { rows: CanonEntry[] }) {
	const [filter, setFilter] = useState("");
	const q = filter.trim().toLowerCase();
	const shown = q
		? rows.filter((e) => `${e.title} ${e.year ?? ""}`.toLowerCase().includes(q))
		: rows;
	if (rows.length === 0) {
		return (
			<p className="text-sm text-slate-500" data-testid="canon-empty">
				Nothing missing. Impressive shelf.
			</p>
		);
	}
	return (
		<div>
			<div className="flex items-center gap-2 mb-3 flex-wrap">
				<label className="relative">
					<Search className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
					<input
						type="search"
						value={filter}
						onChange={(e) => setFilter(e.target.value)}
						placeholder="Filter missing…"
						data-testid="canon-filter"
						className="pl-8 pr-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-amber/40"
					/>
				</label>
				<span className="text-xs text-slate-500" data-testid="canon-missing-count">
					{shown.length} of {rows.length} missing
				</span>
			</div>
			<div className="overflow-x-auto rounded-xl glass-panel border border-slate-600/50">
				<table className="w-full text-sm">
					<thead>
						<tr className="border-b border-slate-700/60">
							<th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-amber">
								Missing
							</th>
							<th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-amber">
								Get it
							</th>
						</tr>
					</thead>
					<tbody className="divide-y divide-slate-700/50">
						{shown.map((e, i) => (
							<tr key={`${e.title}-${e.year ?? ""}-${i}`} data-testid={`canon-missing-${i}`}>
								<td className="px-4 py-2 align-top">
									<span className="text-slate-200">{e.title}</span>
									{entrySub(e) && (
										<span className="block text-xs text-slate-500">{entrySub(e)}</span>
									)}
								</td>
								<td className="px-4 py-2 align-top whitespace-nowrap text-xs text-slate-500">
									Buy / source
								</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>
		</div>
	);
}

export default function CanonPage() {
	const [tab, setTab] = useState<CanonId>("oscars");
	const [result, setResult] = useState<CanonResult | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [limit, setLimit] = useState(25);
	const [media, setMedia] = useState<"movie" | "show" | "both">("both");
	const [paste, setPaste] = useState("");
	const [showOwned, setShowOwned] = useState(false);

	const load = useCallback(async () => {
		if (tab === "paste") {
			setLoading(false);
			return;
		}
		setLoading(true);
		setError(null);
		setResult(null);
		try {
			if (tab === "oscars") setResult(await canonOscars(limit));
			else if (tab === "afi") setResult(await canonAfi(limit));
			else setResult(await canonTmdb(media, limit));
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e));
		} finally {
			setLoading(false);
		}
	}, [tab, limit, media]);

	useEffect(() => {
		setShowOwned(false);
		load();
	}, [load]);

	const runPaste = async () => {
		const items = paste
			.split("\n")
			.map((line) => line.trim())
			.filter(Boolean)
			.map((line) => {
				const m = line.match(/^(.*?)\s*\((\d{4})\)\s*$/);
				return m ? { title: m[1].trim(), year: Number(m[2]) } : { title: line };
			});
		if (items.length === 0) {
			setError("Paste at least one title (one per line, optional year in parentheses).");
			return;
		}
		setLoading(true);
		setError(null);
		try {
			setResult(await canonCheckList(items.slice(0, 200)));
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e));
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="container mx-auto p-6 max-w-6xl" data-testid="canon-page">
			<div className="flex items-start gap-3 mb-2">
				<Award className="w-7 h-7 text-amber shrink-0 mt-0.5" />
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Canon coverage</h1>
					<p className="text-slate-500 mt-1 text-sm">
						What the canon holds that your shelves don&apos;t — the gap finder. Live lists are
						fetched fresh (Oscars, AFI, TMDB); pasted lists never leave matching.
					</p>
				</div>
			</div>

			<div className="mt-4 flex flex-wrap gap-1 border-b border-slate-600/50 pb-px">
				{TABS.map((t) => (
					<button
						key={t.id}
						type="button"
						onClick={() => {
							setTab(t.id);
							setError(null);
						}}
						data-testid={`canon-tab-${t.id}`}
						title={t.hint}
						className={`px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors border border-b-0 -mb-px ${
							tab === t.id
								? "bg-slate-800/90 text-amber border-slate-600/60"
								: "bg-transparent text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/40"
						}`}
					>
						{t.label}
					</button>
				))}
			</div>

			{tab !== "paste" && (
				<div className="mt-4 flex flex-wrap items-center gap-2">
					<label className="text-xs text-slate-500">
						Check first{" "}
						<select
							value={limit}
							onChange={(e) => setLimit(Number(e.target.value))}
							data-testid="canon-limit"
							className="px-2 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 focus:outline-none focus:border-amber/40"
						>
							{LIMITS.map((l) => (
								<option key={l} value={l}>
									{l}
								</option>
							))}
						</select>
					</label>
					{tab === "tmdb" && (
						<label className="text-xs text-slate-500">
							Media{" "}
							<select
								value={media}
								onChange={(e) => setMedia(e.target.value as "movie" | "show" | "both")}
								data-testid="canon-media"
								className="px-2 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 focus:outline-none focus:border-amber/40"
							>
								<option value="both">Movies + TV</option>
								<option value="movie">Movies</option>
								<option value="show">TV</option>
							</select>
						</label>
					)}
					<button
						type="button"
						onClick={load}
						data-testid="canon-refresh"
						className="px-4 py-1.5 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
					>
						Refresh
					</button>
				</div>
			)}

			{tab === "paste" && (
				<div
					className="mt-4 rounded-xl glass-panel border border-slate-600/50 p-4"
					data-testid="canon-paste"
				>
					<p className="text-sm text-slate-400 mb-2">
						One title per line, optional year in parentheses — a 1001-Movies slice, a book appendix,
						an article ranking. Nothing is fetched; only matching runs.
					</p>
					<textarea
						value={paste}
						onChange={(e) => setPaste(e.target.value)}
						rows={8}
						placeholder={"Stalker (1979)\nMulholland Drive (2001)\nPerfect Blue"}
						data-testid="canon-paste-input"
						className="w-full px-3 py-2 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-amber/40 font-mono"
					/>
					<button
						type="button"
						onClick={runPaste}
						data-testid="canon-paste-run"
						className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-amber text-slate-950 text-sm font-semibold hover:bg-amber/90 transition-colors"
					>
						<Clapperboard className="w-4 h-4" />
						Check my list
					</button>
				</div>
			)}

			<div className="mt-6">
				{loading ? (
					<p className="text-slate-500" data-testid="canon-loading">
						Checking holdings…
					</p>
				) : error ? (
					<div data-testid="canon-error">
						<ErrorBanner title="Canon check failed" message={error} hint={BACKEND_DOWN_HINT} />
						<button
							type="button"
							onClick={() => (tab === "paste" ? runPaste() : load())}
							className="mt-3 px-4 py-2 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
						>
							Retry
						</button>
					</div>
				) : result ? (
					<div className="space-y-6">
						<p className="text-sm text-slate-400" data-testid="canon-summary">
							{result.missing_count ?? result.missing.length} missing ·{" "}
							{result.owned_count ?? result.owned.length} held
							{result.checked != null ? ` · ${result.checked} checked` : ""}
						</p>
						<MissingTable rows={result.missing} />
						<div>
							<button
								type="button"
								onClick={() => setShowOwned((v) => !v)}
								data-testid="canon-owned-toggle"
								className="text-sm text-amber hover:underline"
							>
								{showOwned ? "Hide" : "Show"} held ({result.owned.length})
							</button>
							{showOwned && (
								<ul className="mt-2 grid sm:grid-cols-2 gap-2">
									{result.owned.map((e, i) => (
										<li
											key={`${e.title}-${i}`}
											className="px-3 py-2 rounded-lg border border-slate-600/50 text-sm text-slate-300"
										>
											{e.title}
											{e.year != null && <span className="text-slate-500"> ({e.year})</span>}
										</li>
									))}
								</ul>
							)}
						</div>
					</div>
				) : null}
			</div>
		</div>
	);
}
