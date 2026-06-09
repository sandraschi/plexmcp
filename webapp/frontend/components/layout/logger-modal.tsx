"use client";

import { getLogs } from "@/utils/api";
import { useEffect, useState } from "react";

interface LoggerModalProps {
	onClose: () => void;
}

export function LoggerModal({ onClose }: LoggerModalProps) {
	const [lines, setLines] = useState<string[]>([]);
	const [file, setFile] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [tail, setTail] = useState(500);
	const [filter, setFilter] = useState("");
	const [level, setLevel] = useState("");

	const load = () => {
		getLogs({ tail, filter: filter || undefined, level: level || undefined })
			.then(
				(data: {
					lines?: string[];
					file?: string | null;
					error?: string | null;
				}) => {
					setLines(data.lines ?? []);
					setFile(data.file ?? null);
					setError(data.error ?? null);
				},
			)
			.catch((e) => {
				setError(e instanceof Error ? e.message : "Failed to load");
				setLines([]);
				setFile(null);
			});
	};

	useEffect(() => {
		load();
	}, [tail, level]);

	return (
		<div
			className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm"
			onClick={onClose}
		>
			<div
				className="glass-panel-strong rounded-xl shadow-xl max-w-3xl w-full max-h-[85vh] flex flex-col border border-slate-600/50"
				onClick={(e) => e.stopPropagation()}
			>
				<div className="flex items-center justify-between flex-wrap gap-2 p-4 border-b border-slate-600/50">
					<h2 className="text-lg font-semibold text-amber">Logs</h2>
					<div className="flex flex-wrap items-center gap-2">
						<select
							value={level}
							onChange={(e) => setLevel(e.target.value)}
							title="Log Level"
							aria-label="Log Level"
							className="px-2 py-1 rounded bg-slate-700 text-slate-200 text-sm"
						>
							<option value="">All levels</option>
							<option value="DEBUG">DEBUG</option>
							<option value="INFO">INFO</option>
							<option value="WARNING">WARNING</option>
							<option value="ERROR">ERROR</option>
						</select>
						<select
							value={tail}
							onChange={(e) => setTail(Number(e.target.value))}
							title="Number of lines to show"
							aria-label="Number of lines to show"
							className="px-2 py-1 rounded bg-slate-700 text-slate-200 text-sm"
						>
							<option value={100}>100 lines</option>
							<option value={500}>500 lines</option>
							<option value={1000}>1000 lines</option>
							<option value={5000}>5000 lines</option>
						</select>
						<input
							type="text"
							placeholder="Filter..."
							title="Filter logs"
							aria-label="Filter logs"
							value={filter}
							onChange={(e) => setFilter(e.target.value)}
							onKeyDown={(e) => e.key === "Enter" && load()}
							className="px-2 py-1 rounded bg-slate-700 text-slate-200 text-sm w-28"
						/>
						<button
							type="button"
							onClick={load}
							className="px-2 py-1 rounded bg-slate-600 text-slate-200 text-sm hover:bg-slate-500"
						>
							Refresh
						</button>
						<button type="button" onClick={onClose} className="text-slate-400 hover:text-white">
							Close
						</button>
					</div>
				</div>
				{file && <p className="px-4 py-1 text-xs text-slate-500 truncate">{file}</p>}
				<pre className="p-4 overflow-auto text-sm text-slate-300 whitespace-pre-wrap font-mono flex-1 min-h-0">
					{error || lines.join("") || "No log file found."}
				</pre>
			</div>
		</div>
	);
}
