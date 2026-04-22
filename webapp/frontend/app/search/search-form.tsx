"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export function SearchForm({
	query: initialQuery,
	libraryId,
	mode: initialMode = "context",
}: {
	query?: string;
	libraryId?: string;
	mode?: "context" | "dialogue";
}) {
	const router = useRouter();
	const searchParams = useSearchParams();
	const [query, setQuery] = useState(initialQuery ?? "");
	const [mode, setMode] = useState<"context" | "dialogue">(initialMode);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		const params = new URLSearchParams(searchParams);
		if (query) params.set("query", query);
		else params.delete("query");
		if (libraryId) params.set("library_id", libraryId);
		else params.delete("library_id");
		params.set("mode", mode);
		router.push(`/search?${params.toString()}`);
	};

	return (
		<div className="flex flex-col gap-4 max-w-xl">
			<form onSubmit={handleSubmit} className="flex gap-2">
				<input
					type="text"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					placeholder={
						mode === "context" ? "Search movies, shows, music..." : "Search dialogue and quotes..."
					}
					className="flex-1 px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 focus:border-amber/50 focus:outline-none transition-all"
				/>
				<button
					type="submit"
					className={`px-4 py-2 rounded-lg font-medium transition-colors ${
						mode === "context"
							? "bg-amber text-slate-900 hover:bg-amber/90"
							: "bg-purple-600 text-white hover:bg-purple-500"
					}`}
				>
					Search
				</button>
			</form>

			<div className="flex gap-4 items-center pl-1">
				<button
					onClick={() => setMode("context")}
					className={`text-xs font-bold uppercase tracking-widest flex items-center gap-1.5 transition-colors ${mode === "context" ? "text-amber" : "text-slate-500 hover:text-slate-400"}`}
				>
					<div
						className={`w-2 h-2 rounded-full ${mode === "context" ? "bg-amber" : "bg-slate-700"}`}
					/>
					Metadata
				</button>
				<button
					onClick={() => setMode("dialogue")}
					className={`text-xs font-bold uppercase tracking-widest flex items-center gap-1.5 transition-colors ${mode === "dialogue" ? "text-purple-400" : "text-slate-500 hover:text-slate-400"}`}
				>
					<div
						className={`w-2 h-2 rounded-full ${mode === "dialogue" ? "bg-purple-500" : "bg-slate-700"}`}
					/>
					Dialogue
				</button>
			</div>
		</div>
	);
}
