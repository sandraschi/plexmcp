import { listLibraries, getMovies } from "@/utils/api";
import { ErrorBanner } from "@/components/ui/error-banner";
import { MoviesClient } from "./movies-client";

const DEFAULT_LIMIT = 24;

export default async function MoviesPage({
  searchParams,
}: {
  searchParams: Promise<{ library_id?: string; page?: string; limit?: string }>;
}) {
  const params = await searchParams;
  const page = Math.max(1, parseInt(params.page ?? "1", 10) || 1);
  const limit = Math.min(200, Math.max(1, parseInt(params.limit ?? String(DEFAULT_LIMIT), 10) || DEFAULT_LIMIT));
  const offset = (page - 1) * limit;

  let libraries: { key?: string; title?: string; type?: string }[] = [];
  let moviesData: { success?: boolean; data?: unknown[]; results?: unknown[]; error?: string } | null = null;

  try {
    const libRes = await listLibraries();
    if (libRes?.success !== false && Array.isArray(libRes?.data)) {
      libraries = libRes.data as { key?: string; title?: string; type?: string }[];
    }
  } catch {
    libraries = [];
  }

  try {
    moviesData = await getMovies({
      library_id: params.library_id,
      limit,
      offset,
    });
  } catch {
    moviesData = null;
  }

  const movieLibraries = libraries.filter(
    (l) => (l.type ?? "").toLowerCase() === "movie"
  );
  const items =
    moviesData?.data ?? moviesData?.results ?? ([] as unknown[]);
  const hasNext = items.length === limit;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Movies</h1>
      <p className="text-slate-500 mb-6">
        Browse movies from your Plex library. Filter by library below.
      </p>
      {moviesData === null ? (
        <ErrorBanner
          title="Could not load movies"
          message="Backend unavailable or PLEX_TOKEN not configured."
          hint="Set PLEX_TOKEN in webapp/backend/.env"
        />
      ) : moviesData.success === false ? (
        <ErrorBanner
          title="Error"
          message={String(moviesData.error ?? "Unknown error")}
          hint="Check PLEX_TOKEN and PLEX_URL in backend/.env"
        />
      ) : (
        <MoviesClient
          libraries={movieLibraries}
          items={items}
          selectedLibraryId={params.library_id}
          currentPage={page}
          limit={limit}
          hasNext={hasNext}
        />
      )}
    </div>
  );
}
