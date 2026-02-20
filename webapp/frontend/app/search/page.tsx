import { search } from "@/utils/api";
import SearchClient from "./search-client";

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ query?: string; library_id?: string }>;
}) {
  const params = await searchParams;
  let results: any = null;

  if (params.query) {
    try {
      results = await search({
        query: params.query,
        library_id: params.library_id,
        limit: 50,
      });
    } catch (e) {
      console.error("Search error:", e);
      results = [];
    }
  }

  const movies = Array.isArray(results)
    ? results
    : (results?.results || results?.data || []);

  return <SearchClient movies={movies} query={params.query} libraryId={params.library_id} />;
}
