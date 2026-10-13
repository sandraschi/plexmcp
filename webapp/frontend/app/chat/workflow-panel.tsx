"use client";

import { runWorkflow } from "@/utils/api";
import { useState } from "react";

export function WorkflowPanel({ model }: { model: string }) {
	const [query, setQuery] = useState("");
	const [summary, setSummary] = useState<string | null>(null);
	const [count, setCount] = useState<number | null>(null);
	const [busy, setBusy] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const run = async () => {
		if (!query.trim() || busy) return;
		setBusy(true);
		setError(null);
		setSummary(null);
		try {
			const res = await runWorkflow("search_and_summarize", { query: query.trim(), model });
			const items = res?.search_result?.data ?? res?.search_result?.results ?? [];
			setCount(Array.isArray(items) ? items.length : null);
			setSummary(
				typeof res?.summary === "string" ? res.summary : (res?.error ?? "No summary returned."),
			);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Workflow failed");
		} finally {
			setBusy(false);
		}
	};

	return (
		<section
			aria-label="Search and summarize workflow"
			className="rounded-xl border border-slate-600/50 bg-slate-900/40 p-3 mb-3"
		>
			<div className="flex flex-wrap items-center gap-2">
				<input
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					onKeyDown={(e) => e.key === "Enter" && void run()}
					placeholder="Summarize a search: e.g. heist movies"
					data-testid="workflow-query"
					className="flex-1 min-w-48 px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber"
				/>
				<button
					type="button"
					onClick={() => void run()}
					disabled={busy || !query.trim()}
					data-testid="workflow-run"
					className="px-4 py-2 rounded-lg bg-slate-700 text-slate-100 text-sm hover:bg-slate-600 disabled:opacity-50"
				>
					{busy ? "Running…" : "Search + summarize"}
				</button>
			</div>
			{error && <p className="text-xs text-red-400 mt-2">{error}</p>}
			{(summary || count != null) && (
				<div data-testid="workflow-result" className="mt-2 text-sm text-slate-300">
					{count != null && <p className="text-xs text-slate-500">{count} result(s) searched.</p>}
					{summary && <p className="whitespace-pre-wrap mt-1">{summary}</p>}
				</div>
			)}
		</section>
	);
}
