"use client";

import clsx from "clsx";
import { useMemo, useState } from "react";

type Tab = "formatted" | "raw";

function humanizeKey(key: string): string {
	return key
		.replace(/_/g, " ")
		.replace(/([a-z])([A-Z])/g, "$1 $2")
		.replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatBytes(n: number): string {
	if (!Number.isFinite(n) || n < 0) return String(n);
	const units = ["B", "KB", "MB", "GB", "TB"];
	let v = n;
	let i = 0;
	while (v >= 1024 && i < units.length - 1) {
		v /= 1024;
		i += 1;
	}
	return `${v < 10 && i > 0 ? v.toFixed(1) : Math.round(v)} ${units[i]}`;
}

function formatScalar(key: string, value: unknown): string {
	if (value === null || value === undefined) return "—";
	if (typeof value === "boolean") return value ? "Yes" : "No";
	if (typeof value === "number") {
		const kl = key.toLowerCase();
		if (
			kl.includes("timestamp") ||
			kl === "updated_at" ||
			kl === "created_at" ||
			kl === "added_at"
		) {
			const ms = value > 1e12 ? value : value * 1000;
			try {
				return new Date(ms).toLocaleString();
			} catch {
				return String(value);
			}
		}
		if (kl.includes("size") && kl !== "episode_size") {
			return formatBytes(value);
		}
		return String(value);
	}
	if (typeof value === "string") return value || "—";
	return JSON.stringify(value);
}

function isPlainObject(v: unknown): v is Record<string, unknown> {
	return typeof v === "object" && v !== null && !Array.isArray(v);
}

function StatusGrid({ data }: { data: Record<string, unknown> }) {
	const entries = Object.entries(data).filter(([, v]) => typeof v !== "object" || v === null);
	return (
		<dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 text-sm">
			{entries.map(([key, value]) => (
				<div key={key} className="border-b border-slate-700/50 pb-2 sm:pb-3">
					<dt className="text-slate-500 text-xs font-medium uppercase tracking-wide mb-1">
						{humanizeKey(key)}
					</dt>
					<dd className="text-slate-200 break-words">{formatScalar(key, value)}</dd>
				</div>
			))}
		</dl>
	);
}

function LibrariesTable({ rows }: { rows: Record<string, unknown>[] }) {
	if (rows.length === 0) {
		return <p className="text-slate-500 text-sm">No libraries returned.</p>;
	}
	const preferred = [
		"title",
		"name",
		"type",
		"key",
		"id",
		"uuid",
		"count",
		"agent",
		"scanner",
		"language",
	];
	const keys = new Set<string>();
	for (const r of rows) {
		for (const k of Object.keys(r)) {
			keys.add(k);
		}
	}
	const columns = [
		...preferred.filter((k) => keys.has(k)),
		...[...keys].filter((k) => !preferred.includes(k)),
	];

	return (
		<div className="overflow-x-auto rounded-lg border border-slate-600/40">
			<table className="w-full text-sm text-left">
				<thead>
					<tr className="bg-slate-800/80 text-slate-400 text-xs uppercase tracking-wide">
						{columns.map((c) => (
							<th key={c} className="px-3 py-2 font-medium whitespace-nowrap">
								{humanizeKey(c)}
							</th>
						))}
					</tr>
				</thead>
				<tbody>
					{rows.map((row, i) => (
						<tr key={i} className="border-t border-slate-700/50 hover:bg-slate-800/40">
							{columns.map((c) => (
								<td
									key={c}
									className="px-3 py-2 text-slate-200 whitespace-nowrap max-w-[14rem] truncate"
								>
									{formatScalar(c, row[c])}
								</td>
							))}
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
}

function FormattedPayload({ payload }: { payload: Record<string, unknown> }) {
	const success = payload.success;
	const operation = payload.operation;
	const err = payload.error;
	const errCode = payload.error_code;
	const suggestions = payload.suggestions;

	if (success === false) {
		return (
			<div className="space-y-4">
				<div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3">
					<p className="text-red-300 font-medium">Request failed</p>
					{typeof err === "string" && <p className="text-slate-300 mt-1 text-sm">{err}</p>}
					{typeof errCode === "string" && (
						<p className="text-slate-500 text-xs mt-2 font-mono">Code: {errCode}</p>
					)}
					{Array.isArray(suggestions) && suggestions.length > 0 && (
						<ul className="mt-3 list-disc list-inside text-slate-400 text-sm space-y-1">
							{suggestions.map((s, i) => (
								<li key={i}>{String(s)}</li>
							))}
						</ul>
					)}
				</div>
			</div>
		);
	}

	const data = payload.data;
	if (!isPlainObject(data)) {
		return <p className="text-slate-500 text-sm">No structured data to display.</p>;
	}

	const status = data.status;
	const libraries = data.libraries;

	return (
		<div className="space-y-8">
			{(typeof operation === "string" || success === true) && (
				<div className="flex flex-wrap gap-3 text-xs text-slate-500">
					{typeof operation === "string" && (
						<span>
							Operation: <span className="text-amber font-mono">{operation}</span>
						</span>
					)}
					{success === true && <span className="text-emerald-500/90">Connected</span>}
				</div>
			)}

			{isPlainObject(status) && (
				<section>
					<h2 className="text-lg font-semibold text-slate-100 mb-3 flex items-center gap-2">
						Plex server
						<span className="text-slate-500 font-normal text-sm">(status)</span>
					</h2>
					<div className="glass-panel rounded-xl p-4">
						<StatusGrid data={status} />
					</div>
				</section>
			)}

			{Array.isArray(libraries) && (
				<section>
					<h2 className="text-lg font-semibold text-slate-100 mb-3">
						Libraries
						<span className="text-slate-500 font-normal text-sm ml-2">({libraries.length})</span>
					</h2>
					<div className="glass-panel rounded-xl p-4">
						{libraries.length === 0 ? (
							<p className="text-slate-500 text-sm">No libraries reported.</p>
						) : libraries.every(isPlainObject) ? (
							<LibrariesTable rows={libraries as Record<string, unknown>[]} />
						) : (
							<pre className="text-xs text-slate-400 overflow-auto font-mono">
								{JSON.stringify(libraries, null, 2)}
							</pre>
						)}
					</div>
				</section>
			)}

			{!isPlainObject(status) && libraries === undefined && (
				<p className="text-slate-500 text-sm">
					No server status block in this response. Switch to{" "}
					<strong className="text-slate-300">Raw JSON</strong> to inspect.
				</p>
			)}
		</div>
	);
}

export function ServerInfoView({ payload }: { payload: Record<string, unknown> }) {
	const [tab, setTab] = useState<Tab>("formatted");

	const rawJson = useMemo(() => JSON.stringify(payload, null, 2), [payload]);

	return (
		<div className="space-y-4">
			<div className="flex flex-wrap gap-1 border-b border-slate-600/50 pb-px">
				{(
					[
						["formatted", "Overview"],
						["raw", "Raw JSON"],
					] as const
				).map(([id, label]) => (
					<button
						key={id}
						type="button"
						onClick={() => setTab(id)}
						className={clsx(
							"px-4 py-2.5 text-sm font-medium rounded-t-lg transition-colors border border-b-0 -mb-px",
							tab === id
								? "bg-slate-800/90 text-amber border-slate-600/60"
								: "bg-transparent text-slate-500 border-transparent hover:text-slate-300 hover:bg-slate-800/40",
						)}
					>
						{label}
					</button>
				))}
			</div>

			{tab === "formatted" ? (
				<FormattedPayload payload={payload} />
			) : (
				<pre className="p-4 rounded-xl glass-panel text-xs text-slate-300 overflow-auto max-h-[70vh] font-mono leading-relaxed">
					{rawJson}
				</pre>
			)}
		</div>
	);
}
