"use client";

import { type DiagnosticsResponse, getDiagnostics } from "@/utils/api";
import { useEffect, useState } from "react";

const dot: Record<string, string> = {
	ok: "bg-green-500",
	warn: "bg-amber-500",
	error: "bg-red-500",
	info: "bg-slate-500",
};

export function DiagnosticsPanel() {
	const [data, setData] = useState<DiagnosticsResponse | null>(null);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		let cancelled = false;
		getDiagnostics()
			.then((d) => {
				if (!cancelled) setData(d);
			})
			.catch((e: Error) => {
				if (!cancelled) setError(e.message);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	return (
		<section
			aria-label="Diagnostics"
			className="rounded-xl glass-panel border border-slate-600/50 p-4 mb-6"
		>
			<div className="flex items-center justify-between mb-3">
				<h2 className="font-medium text-slate-200">Diagnostics</h2>
				{data && (
					<span data-testid="diagnostics-overall" className="text-xs text-slate-400">
						Overall: {data.overall}
					</span>
				)}
			</div>
			{error ? (
				<p className="text-sm text-slate-500">Diagnostics unavailable: {error}</p>
			) : !data ? (
				<p className="text-sm text-slate-500">Checking Plex, LLM, RAG, *arr…</p>
			) : (
				<ul data-testid="diagnostics-list" className="space-y-2">
					{data.checks.map((c) => (
						<li key={c.id} className="flex items-start gap-2 text-sm">
							<span
								className={`mt-1.5 w-2.5 h-2.5 rounded-full shrink-0 ${dot[c.status] ?? "bg-slate-500"}`}
							/>
							<span>
								<span className="text-slate-200 font-medium">{c.label}</span>
								<span className="text-slate-500"> — {c.message}</span>
							</span>
						</li>
					))}
				</ul>
			)}
		</section>
	);
}
