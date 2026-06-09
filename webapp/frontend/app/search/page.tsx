"use client";

import { getSemanticSearch, getSettings, search } from "@/utils/api";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import SearchClient from "./search-client";

function SearchPageInner() {
	const searchParams = useSearchParams();
	const query = searchParams?.get("query") ?? undefined;
	const libraryId = searchParams?.get("library_id") ?? undefined;
	const mode = searchParams?.get("mode") || "context";

	const [results, setResults] = useState<unknown[]>([]);
	const [plexUrl, setPlexUrl] = useState<string | null>(null);
	const [loading, setLoading] = useState(Boolean(query));

	useEffect(() => {
		let cancelled = false;
		(async () => {
			try {
				const settings = await getSettings();
				const url = settings?.plex_url;
				if (!cancelled) {
					setPlexUrl(typeof url === "string" && url.trim() ? url.trim() : null);
				}
			} catch {
				if (!cancelled) setPlexUrl(null);
			}

			if (!query) {
				if (!cancelled) {
					setResults([]);
					setLoading(false);
				}
				return;
			}

			setLoading(true);
			try {
				if (mode === "dialogue") {
					const semantic = await getSemanticSearch({
						query,
						limit: 50,
						index: "subtitles",
					});
					if (!cancelled) setResults(semantic.results ?? []);
				} else {
					const res = await search({
						query,
						library_id: libraryId,
						limit: 50,
					});
					const movies = Array.isArray(res)
						? res
						: res?.results || res?.data || [];
					if (!cancelled) setResults(movies);
				}
			} catch {
				if (!cancelled) setResults([]);
			} finally {
				if (!cancelled) setLoading(false);
			}
		})();
		return () => {
			cancelled = true;
		};
	}, [query, libraryId, mode]);

	if (loading && query) {
		return (
			<div className="container mx-auto p-6">
				<p className="text-slate-400">Searching…</p>
			</div>
		);
	}

	return (
		<SearchClient
			results={results}
			query={query}
			libraryId={libraryId}
			mode={mode}
			plexUrl={plexUrl}
		/>
	);
}

export default function SearchPage() {
	return (
		<Suspense
			fallback={
				<div className="container mx-auto p-6">
					<p className="text-slate-400">Loading…</p>
				</div>
			}
		>
			<SearchPageInner />
		</Suspense>
	);
}
