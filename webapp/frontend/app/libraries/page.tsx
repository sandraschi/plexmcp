import Link from "next/link";
import { listLibraries } from "@/lib/api";
import { ErrorBanner } from "@/components/ui/error-banner";

export default async function LibrariesPage() {
  let data: { success?: boolean; data?: { key?: string; title?: string; type?: string }[]; error?: string } | null =
    null;
  try {
    data = await listLibraries();
  } catch {
    data = null;
  }

  const libraries = (data?.data ?? []) as { key?: string; title?: string; type?: string }[];

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>
      {data === null ? (
        <ErrorBanner
          title="Could not load libraries"
          message="Backend unavailable or PLEX_TOKEN not configured."
          hint="Set PLEX_TOKEN in webapp/backend/.env"
        />
      ) : !data.success ? (
        <ErrorBanner
          title="Error"
          message={String(data.error ?? "Unknown error")}
          hint="Check PLEX_TOKEN and PLEX_URL in backend/.env"
        />
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {libraries.map((lib: { key?: string; title?: string; type?: string }) => (
            <Link
              key={lib.key ?? lib.title ?? String(Math.random())}
              href={`/search?library_id=${lib.key ?? ""}`}
              className="block p-6 rounded-xl glass-panel border-slate-600/50 hover:border-amber/40 transition-colors"
            >
              <p className="text-xl font-semibold text-slate-100">{lib.title ?? "Library"}</p>
              <p className="text-sm text-slate-400">{lib.type ?? ""}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
