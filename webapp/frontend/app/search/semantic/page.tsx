"use client";

import { useState } from "react";
import { getSemanticSearch, syncRag, type SemanticResult } from "@/utils/api";
import { Search, AlertCircle, Film, RefreshCw } from "lucide-react";

function ResultCard({ r }: { r: SemanticResult }) {
  const title = r.metadata?.title ?? (r.content ?? r.text ?? "").slice(0, 80);
  const body = r.content ?? r.text ?? "";
  const meta = r.metadata;
  return (
    <div className="glass-panel p-4 rounded-lg border border-slate-600/50">
      <div className="flex items-center gap-2 text-amber font-medium">
        <Film className="w-4 h-4 shrink-0" />
        {title}
      </div>
      {meta?.year && (
        <div className="text-slate-400 text-sm mt-1">
          {meta.library && `${meta.library} · `}
          {meta.type && `${meta.type} · `}
          {meta.year}
        </div>
      )}
      {body && (
        <p className="text-slate-300 text-sm mt-2 line-clamp-3">{body}</p>
      )}
      {typeof r.score === "number" && (
        <p className="text-slate-500 text-xs mt-1">Score: {r.score.toFixed(3)}</p>
      )}
    </div>
  );
}

export default function SemanticSearchPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [available, setAvailable] = useState<boolean | null>(null);
  const [results, setResults] = useState<SemanticResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncResult, setSyncResult] = useState<{ count: number; error?: string } | null>(null);

  async function handleSync() {
    setSyncLoading(true);
    setSyncResult(null);
    try {
      const data = await syncRag();
      if (data.success) {
        setSyncResult({ count: data.indexed_count });
        setAvailable(true);
      } else {
        setSyncResult({ count: 0, error: data.error ?? "Sync failed" });
      }
    } catch (e) {
      setSyncResult({ count: 0, error: e instanceof Error ? e.message : "Request failed" });
    } finally {
      setSyncLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResults([]);
    setAvailable(null);
    try {
      const data = await getSemanticSearch({ query: query.trim(), limit: 20 });
      setAvailable(data.available);
      setResults(data.results ?? []);
      if (data.error) setError(data.error);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setAvailable(false);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-slate-100 flex items-center gap-2">
        <Search className="w-7 h-7 text-amber" />
        Semantic search
      </h1>
      <p className="text-slate-400 text-sm">
        Natural-language search over indexed Plex metadata (RAG). Index once with the button
        below (or via MCP <code className="text-amber/80">plex_rag(operation=&quot;sync_metadata&quot;)</code>).
      </p>

      <div className="flex flex-wrap items-center gap-3 p-4 rounded-lg bg-slate-800/50 border border-slate-600/50">
        <button
          type="button"
          onClick={handleSync}
          disabled={syncLoading}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700 text-slate-200 font-medium hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RefreshCw className={`w-4 h-4 ${syncLoading ? "animate-spin" : ""}`} />
          {syncLoading ? "Indexing…" : "Sync / Index metadata"}
        </button>
        {syncResult && (
          <span className="text-sm text-slate-400">
            {syncResult.error
              ? `Error: ${syncResult.error}`
              : `Indexed ${syncResult.count} item(s). You can search now.`}
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 flex-wrap">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. sci-fi movies from the 80s, romantic comedies"
          className="flex-1 min-w-[200px] px-4 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 focus:border-amber/50 focus:ring-1 focus:ring-amber/30"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="px-4 py-2 rounded-lg bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {available === false && (error || results.length === 0) && (
        <div className="flex items-start gap-2 p-4 rounded-lg bg-slate-800/80 border border-amber/30 text-amber">
          <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">RAG unavailable</p>
            <p className="text-sm text-slate-300 mt-1">
              Semantic search requires the mcp-central-docs <strong>source</strong> to be on the
              Python path (same machine as Plex MCP). The mcp-central-docs MCP server does not
              need to be running. Run <code>plex_rag(operation=&quot;sync_metadata&quot;)</code> once to index.
            </p>
            {error && <p className="text-sm text-slate-400 mt-1">{error}</p>}
          </div>
        </div>
      )}

      {available === true && results.length === 0 && !loading && (
        <p className="text-slate-400">No results. Try a different query or sync metadata first.</p>
      )}

      {results.length > 0 && (
        <div className="space-y-3">
          <p className="text-slate-400 text-sm">{results.length} result(s)</p>
          <div className="grid gap-3 sm:grid-cols-2">
            {results.map((r, i) => (
              <ResultCard key={i} r={r} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
