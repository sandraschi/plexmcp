"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import { getMovies, getSettings, listLibraries } from "@/utils/api";
import { PLEX_AUTH_HINT, PLEX_TOKEN_HINT } from "@/utils/config-hints";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { MoviesClient } from "./movies-client";

const DEFAULT_LIMIT = 24;

function MoviesPageInner() {
	const searchParams = useSearchParams();
	const libraryId = searchParams?.get("library_id") ?? undefined;
	const page = Math.max(1, Number.parseInt(searchParams?.get("page") ?? "1", 10) || 1);
	const limit = Math.min(
		200,
		Math.max(
			1,
			Number.parseInt(searchParams?.get("limit") ?? String(DEFAULT_LIMIT), 10) || DEFAULT_LIMIT,
		),
	);
	const offset = (page - 1) * limit;

	const [libraries, setLibraries] = useState<{ key?: string; title?: string; type?: string }[]>([]);
	const [moviesData, setMoviesData] = useState<{
		success?: boolean;
		data?: unknown[];
		results?: unknown[];
		error?: string;
	} | null>(null);
	const [plexUrl, setPlexUrl] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		let cancelled = false;
		setLoading(true);
		(async () => {
			let nextPlexUrl: string | null = null;
			let nextLibraries: { key?: string; title?: string; type?: string }[] = [];
			let nextMovies: typeof moviesData = null;

			try {
				const settings = await getSettings();
				const url = settings?.plex_url;
				nextPlexUrl = typeof url === "string" && url.trim() ? url.trim() : null;
			} catch {
				nextPlexUrl = null;
			}

			try {
				const libRes = await listLibraries();
				if (libRes?.success !== false && Array.isArray(libRes?.data)) {
					nextLibraries = libRes.data as {
						key?: string;
						title?: string;
						type?: string;
					}[];
				}
			} catch {
				nextLibraries = [];
			}

			try {
				nextMovies = await getMovies({
					library_id: libraryId,
					limit,
					offset,
				});
			} catch {
				nextMovies = null;
			}

			if (!cancelled) {
				setPlexUrl(nextPlexUrl);
				setLibraries(nextLibraries);
				setMoviesData(nextMovies);
				setLoading(false);
			}
		})();
		return () => {
			cancelled = true;
		};
	}, [libraryId, limit, offset]);

	const movieLibraries = libraries.filter((l) => (l.type ?? "").toLowerCase() === "movie");
	const items = moviesData?.data ?? moviesData?.results ?? ([] as unknown[]);
	const hasNext = items.length === limit;

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-2 text-slate-100">Movies</h1>
			<p className="text-slate-500 mb-6">
				Browse movies from your Plex library. Filter by library below.
				{libraryId ? (
					<>
						{" "}
						<Link
							href={`/libraries?library_id=${encodeURIComponent(libraryId)}`}
							className="text-amber/90 hover:text-amber underline underline-offset-2"
						>
							Back to libraries
						</Link>
					</>
				) : null}
			</p>
			{loading ? (
				<p className="text-slate-400">Loading movies…</p>
			) : moviesData === null ? (
				<ErrorBanner
					title="Could not load movies"
					message="Backend unavailable or Plex not configured."
					hint={PLEX_TOKEN_HINT}
					actionHref="/settings"
					actionLabel="Open Settings → Plex"
				/>
			) : moviesData.success === false ? (
				<ErrorBanner
					title="Error"
					message={String(moviesData.error ?? "Unknown error")}
					hint={PLEX_AUTH_HINT}
					actionHref="/settings"
					actionLabel="Check Settings → Plex"
				/>
			) : (
				<MoviesClient
					libraries={movieLibraries}
					items={items}
					selectedLibraryId={libraryId}
					currentPage={page}
					limit={limit}
					hasNext={hasNext}
					plexUrl={plexUrl}
				/>
			)}
		</div>
	);
}

export default function MoviesPage() {
	return (
		<Suspense
			fallback={
				<div className="container mx-auto p-6">
					<p className="text-slate-400">Loading…</p>
				</div>
			}
		>
			<MoviesPageInner />
		</Suspense>
	);
}
