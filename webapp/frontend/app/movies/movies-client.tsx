"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";

const VIEW_KEY = "plex-webapp-movies-view";
type ViewMode = "card" | "list";

interface Lib {
  key?: string;
  title?: string;
  type?: string;
}

interface MoviesClientProps {
  libraries: Lib[];
  items: unknown[];
  selectedLibraryId?: string;
  currentPage: number;
  limit: number;
  hasNext: boolean;
}

function MovieItem({
  item,
  index,
  view,
}: {
  item: Record<string, unknown>;
  index: number;
  view: ViewMode;
}) {
  const title = String(item?.title ?? item?.name ?? "Unknown");
  const year = item?.year ?? (item as { year?: string })?.year?.toString();
  const summary = item?.summary ?? item?.plot;
  const key = String(item?.key ?? item?.ratingKey ?? index);

  if (view === "list") {
    return (
      <div
        key={key}
        className="flex flex-wrap items-baseline gap-x-3 gap-y-1 rounded-lg glass-panel border border-slate-600/50 px-4 py-3 hover:border-amber/40 transition-colors"
      >
        <p className="font-semibold text-slate-200 shrink-0 min-w-[120px]">
          {title}
        </p>
        {year != null && (
          <span className="text-sm text-slate-500">{String(year)}</span>
        )}
        {summary != null && (
          <p className="text-sm text-slate-400 flex-1 min-w-0 line-clamp-1">
            {String(summary)}
          </p>
        )}
      </div>
    );
  }

  return (
    <div
      key={key}
      className="rounded-xl glass-panel border border-slate-600/50 p-4 hover:border-amber/40 transition-colors"
    >
      <p className="font-semibold text-slate-200 truncate" title={title}>
        {title}
      </p>
      {year != null && (
        <p className="text-sm text-slate-500">{String(year)}</p>
      )}
      {summary != null && (
        <p className="text-xs text-slate-400 mt-1 line-clamp-2">
          {String(summary)}
        </p>
      )}
    </div>
  );
}

export function MoviesClient({
  libraries,
  items,
  selectedLibraryId,
  currentPage,
  limit,
  hasNext,
}: MoviesClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [viewMode, setViewMode] = useState<ViewMode>("card");

  useEffect(() => {
    const stored = localStorage.getItem(VIEW_KEY);
    if (stored === "list" || stored === "card") setViewMode(stored);
  }, []);

  const updateView = (v: ViewMode) => {
    setViewMode(v);
    if (typeof window !== "undefined") localStorage.setItem(VIEW_KEY, v);
  };

  const setPage = (page: number) => {
    const next = new URLSearchParams(searchParams?.toString() ?? "");
    next.set("page", String(page));
    if (limit !== 24) next.set("limit", String(limit));
    router.push(`/movies?${next.toString()}`);
  };

  const handleLibraryChange = (libraryId: string) => {
    const next = new URLSearchParams(searchParams?.toString() ?? "");
    if (libraryId) next.set("library_id", libraryId);
    else next.delete("library_id");
    next.delete("page");
    router.push(`/movies?${next.toString()}`);
  };

  return (
    <>
      <div className="mb-6 flex flex-wrap items-center gap-4">
        {libraries.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm text-slate-400">Library:</label>
            <select
              value={selectedLibraryId ?? ""}
              onChange={(e) => handleLibraryChange(e.target.value)}
              className="px-3 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm min-w-[180px]"
            >
              <option value="">All movie libraries</option>
              {libraries.map((lib) => (
                <option key={lib.key ?? lib.title} value={lib.key ?? ""}>
                  {lib.title ?? lib.key ?? "Library"}
                </option>
              ))}
            </select>
          </div>
        )}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-sm text-slate-400">View:</span>
          <button
            type="button"
            onClick={() => updateView("card")}
            className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
              viewMode === "card"
                ? "bg-amber/20 border-amber/50 text-amber"
                : "glass-panel border-slate-600/50 text-slate-400 hover:text-slate-200"
            }`}
          >
            Cards
          </button>
          <button
            type="button"
            onClick={() => updateView("list")}
            className={`px-3 py-1.5 rounded-lg text-sm border transition-colors ${
              viewMode === "list"
                ? "bg-amber/20 border-amber/50 text-amber"
                : "glass-panel border-slate-600/50 text-slate-400 hover:text-slate-200"
            }`}
          >
            List
          </button>
        </div>
      </div>

      {viewMode === "card" ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {items.map((item, i) => {
            const row = item as Record<string, unknown>;
            const key = String(row?.key ?? row?.ratingKey ?? i);
            return (
              <MovieItem
                key={key}
                item={row}
                index={i}
                view="card"
              />
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((item, i) => {
            const row = item as Record<string, unknown>;
            const key = String(row?.key ?? row?.ratingKey ?? i);
            return (
              <MovieItem
                key={key}
                item={row}
                index={i}
                view="list"
              />
            );
          })}
        </div>
      )}

      {items.length === 0 && (
        <p className="text-slate-500 py-8">No movies found.</p>
      )}

      {(currentPage > 1 || hasNext) && items.length > 0 && (
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <button
            type="button"
            onClick={() => setPage(currentPage - 1)}
            disabled={currentPage <= 1}
            className="px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber/40"
          >
            Previous
          </button>
          <span className="text-sm text-slate-400">
            Page {currentPage}
            {hasNext ? " (more available)" : ""}
          </span>
          <button
            type="button"
            onClick={() => setPage(currentPage + 1)}
            disabled={!hasNext}
            className="px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:border-amber/40"
          >
            Next
          </button>
        </div>
      )}
    </>
  );
}
