"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export function SearchForm({ query: initialQuery, libraryId }: { query?: string; libraryId?: string }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(initialQuery ?? "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams);
    if (query) params.set("query", query);
    else params.delete("query");
    router.push(`/search?${params.toString()}`);
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 max-w-xl">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search movies, shows, music..."
        className="flex-1 px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 focus:border-amber/50 focus:outline-none"
      />
      <button
        type="submit"
        className="px-4 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 transition-colors"
      >
        Search
      </button>
    </form>
  );
}
