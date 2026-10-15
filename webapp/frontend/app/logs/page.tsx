"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import { getLogs } from "@/utils/api";
import { BACKEND_DOWN_HINT } from "@/utils/config-hints";
import { ScrollText, Search } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

const LEVELS = ["", "DEBUG", "INFO", "WARNING", "ERROR"];
const TAILS = [100, 500, 2000];

export default function LogsPage() {
	const [lines, setLines] = useState<string[] | null>(null);
	const [total, setTotal] = useState(0);
	const [file, setFile] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [filter, setFilter] = useState("");
	const [level, setLevel] = useState("");
	const [tail, setTail] = useState(500);
	const [applied, setApplied] = useState({ filter: "", level: "", tail: 500 });

	const load = useCallback(async (f: string, lv: string, t: number) => {
		setLoading(true);
		setError(null);
		try {
			const data = await getLogs({
				tail: t,
				...(f ? { filter: f } : {}),
				...(lv ? { level: lv } : {}),
			});
			if (data.error) {
				setError(String(data.error));
				setLines([]);
				setTotal(0);
			} else {
				setLines(data.lines ?? []);
				setTotal(data.total ?? 0);
			}
			setFile(data.file ?? null);
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e));
		} finally {
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		load(applied.filter, applied.level, applied.tail);
	}, [applied, load]);

	return (
		<div className="container mx-auto p-6 max-w-6xl" data-testid="logs-page">
			<div className="flex items-start gap-3 mb-2">
				<ScrollText className="w-7 h-7 text-amber shrink-0 mt-0.5" />
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Logs</h1>
					<p className="text-slate-500 mt-1 text-sm">
						Backend log tail{file ? ` · ${file}` : ""} ·{" "}
						<span data-testid="logs-count">{total} matching lines</span>
					</p>
				</div>
			</div>

			<form
				className="mt-4 flex flex-wrap items-center gap-2"
				onSubmit={(e) => {
					e.preventDefault();
					setApplied({ filter, level, tail });
				}}
			>
				<label className="relative">
					<Search className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
					<input
						type="search"
						value={filter}
						onChange={(e) => setFilter(e.target.value)}
						placeholder="Filter substring…"
						data-testid="logs-filter"
						className="pl-8 pr-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-amber/40"
					/>
				</label>
				<select
					value={level}
					onChange={(e) => setLevel(e.target.value)}
					data-testid="logs-level"
					className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 focus:outline-none focus:border-amber/40"
				>
					{LEVELS.map((l) => (
						<option key={l} value={l}>
							{l === "" ? "All levels" : l}
						</option>
					))}
				</select>
				<select
					value={tail}
					onChange={(e) => setTail(Number(e.target.value))}
					data-testid="logs-tail"
					className="px-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 focus:outline-none focus:border-amber/40"
				>
					{TAILS.map((t) => (
						<option key={t} value={t}>
							Last {t}
						</option>
					))}
				</select>
				<button
					type="submit"
					data-testid="logs-apply"
					className="px-4 py-1.5 rounded-lg bg-amber text-slate-950 text-sm font-semibold hover:bg-amber/90 transition-colors"
				>
					Apply
				</button>
				<button
					type="button"
					data-testid="logs-refresh"
					onClick={() => setApplied({ filter, level, tail })}
					className="px-4 py-1.5 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
				>
					Refresh
				</button>
			</form>

			<div className="mt-4">
				{loading ? (
					<p className="text-slate-500" data-testid="logs-loading">
						Loading logs…
					</p>
				) : error ? (
					<div data-testid="logs-error">
						<ErrorBanner title="Logs unavailable" message={error} hint={BACKEND_DOWN_HINT} />
						<button
							type="button"
							onClick={() => setApplied({ filter, level, tail })}
							className="mt-3 px-4 py-2 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
						>
							Retry
						</button>
					</div>
				) : (lines?.length ?? 0) === 0 ? (
					<p className="text-sm text-slate-500" data-testid="logs-empty">
						No log lines match. Clear the filter or pick a lower level.
					</p>
				) : (
					<pre
						data-testid="logs-output"
						className="rounded-xl glass-panel border border-slate-600/50 p-4 text-xs text-slate-300 overflow-auto max-h-[60vh] whitespace-pre-wrap"
					>
						{(lines ?? []).join("")}
					</pre>
				)}
			</div>
		</div>
	);
}
