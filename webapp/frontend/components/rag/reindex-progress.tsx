"use client";

import { useMemo } from "react";
import type { RagSyncProgress } from "@/utils/api";

function progressPercent(p: RagSyncProgress): number {
  switch (p.phase) {
    case "idle":
      return 0;
    case "starting":
      return 8;
    case "scanning":
      return 18;
    case "processing_library": {
      const total = p.libraries_total ?? 1;
      const idx = p.library_index ?? 0;
      return 18 + Math.min(62, (idx / Math.max(total, 1)) * 62);
    }
    case "embedding":
      return 90;
    case "complete":
      return 100;
    case "error":
      return 100;
    default:
      return 40;
  }
}

export function ReindexProgressPanel({ progress }: { progress: RagSyncProgress | null }) {
  const pct = useMemo(() => (progress ? progressPercent(progress) : 0), [progress]);

  if (!progress || progress.phase === "idle") {
    return null;
  }

  const isError = progress.phase === "error";
  const isDone = progress.phase === "complete";

  return (
    <div
      className={`mt-4 rounded-lg border p-4 ${
        isError ? "border-red-900/50 bg-red-950/20" : "border-slate-600/50 bg-slate-900/40"
      }`}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {isDone ? "Finished" : isError ? "Failed" : "Reindex progress"}
        </span>
        {!isDone && !isError && (
          <span className="text-xs text-amber font-mono">{Math.round(pct)}%</span>
        )}
      </div>
      <div className="h-2.5 rounded-full bg-slate-800 overflow-hidden">
        <div
          className={`h-full transition-[width] duration-300 ease-out rounded-full ${
            isError ? "bg-red-500/80" : isDone ? "bg-emerald-500/80" : "bg-amber"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className={`text-sm mt-3 ${isError ? "text-red-300" : "text-slate-300"}`}>
        {progress.message || progress.phase}
      </p>
      {(progress.phase === "processing_library" || progress.phase === "scanning") && (
        <dl className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-1 text-xs text-slate-500">
          {progress.libraries_total != null && progress.libraries_total > 0 && (
            <>
              <div>
                <dt className="inline text-slate-600">Library </dt>
                <dd className="inline text-slate-400">
                  {progress.library_index ?? 0}/{progress.libraries_total}
                  {progress.library_name ? ` — ${progress.library_name}` : ""}
                </dd>
              </div>
              <div>
                <dt className="inline text-slate-600">Documents built </dt>
                <dd className="inline text-slate-400">{progress.documents_so_far ?? 0}</dd>
              </div>
            </>
          )}
        </dl>
      )}
      {progress.phase === "embedding" && progress.documents_total != null && (
        <p className="text-xs text-slate-500 mt-2">
          Embedding {progress.documents_total} chunk(s). This step is CPU-heavy; the UI keeps updating if you leave
          this page open.
        </p>
      )}
    </div>
  );
}
