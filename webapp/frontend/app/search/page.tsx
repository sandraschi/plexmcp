import { getSemanticSearch, getSettings, search } from "@/utils/api";
import SearchClient from "./search-client";

export default async function SearchPage({
	searchParams,
}: {
	searchParams: Promise<{ query?: string; library_id?: string; mode?: string }>;
}) {
	const params = await searchParams;
	let results: any = null;
	const mode = params.mode || "context";
	let plexUrl: string | null = null;
	try {
		const settings = await getSettings();
		const url = settings?.plex_url;
		plexUrl = typeof url === "string" && url.trim() ? url.trim() : null;
	} catch {
		plexUrl = null;
	}

	if (params.query) {
		try {
			if (mode === "dialogue") {
				const semantic = await getSemanticSearch({
					query: params.query,
					limit: 50,
					index: "subtitles",
				});
				results = semantic.results;
			} else {
				results = await search({
					query: params.query,
					library_id: params.library_id,
					limit: 50,
				});
			}
		} catch (e) {
			console.error("Search error:", e);
			results = [];
		}
	}

	const movies = Array.isArray(results) ? results : results?.results || results?.data || [];

	return (
		<SearchClient
			results={movies}
			query={params.query}
			libraryId={params.library_id}
			mode={mode}
			plexUrl={plexUrl}
		/>
	);
}
