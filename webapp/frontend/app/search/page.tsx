import { Suspense } from "react";
import { SearchForm } from "./search-form";
import { search } from "@/lib/api";

function SearchFormSuspense({ query, libraryId }: { query?: string; libraryId?: string }) {
  return (
    <Suspense fallback={<div className="h-10 bg-slate-800 rounded-lg animate-pulse" />}>
      <SearchForm query={query} libraryId={libraryId} />
    </Suspense>
  );
}

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ query?: string; library_id?: string }>;
}) {
  const params = await searchParams;
  let results: unknown = null;
  if (params.query) {
    try {
      results = await search({
        query: params.query,
        library_id: params.library_id,
        limit: 50,
      });
    } catch {
      results = null;
    }
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Search</h1>
      <p className="text-slate-500 mb-6">Keyword search across Plex. Use Chat with RAG for semantic-style context.</p>
      <SearchForm query={params.query} libraryId={params.library_id} />
      {results && (
        <div className="mt-8">
          <pre className="p-4 rounded-xl glass-panel text-sm text-slate-300 overflow-auto max-h-96">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
