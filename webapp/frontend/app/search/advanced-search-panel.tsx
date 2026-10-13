"use client";

import { advancedSearch } from "@/utils/api";
import { useState } from "react";
import MovieCard from "../components/MovieCard";

const inputCls =
	"px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-slate-100 text-sm placeholder-slate-500 focus:border-amber/50 focus:outline-none w-full";

export function AdvancedSearchPanel() {
	const [open, setOpen] = useState(false);
	const [title, setTitle] = useState("");
	const [genre, setGenre] = useState("");
	const [actor, setActor] = useState("");
	const [director, setDirector] = useState("");
	const [collection, setCollection] = useState("");
	const [mediaType, setMediaType] = useState("");
	const [year, setYear] = useState("");
	const [minYear, setMinYear] = useState("");
	const [maxYear, setMaxYear] = useState("");
	const [minRating, setMinRating] = useState("");
	const [maxRating, setMaxRating] = useState("");
	const [unwatched, setUnwatched] = useState(false);
	const [sortBy, setSortBy] = useState("titleSort");
	const [sortDir, setSortDir] = useState("asc");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [results, setResults] = useState<unknown[]>([]);
	const [searched, setSearched] = useState(false);

	const submit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError(null);
		try {
			const num = (v: string) => (v.trim() === "" ? undefined : Number(v));
			const res = await advancedSearch({
				...(title.trim() ? { title: title.trim() } : {}),
				...(genre.trim() ? { genre: genre.trim() } : {}),
				...(actor.trim() ? { actor: actor.trim() } : {}),
				...(director.trim() ? { director: director.trim() } : {}),
				...(collection.trim() ? { collection: collection.trim() } : {}),
				...(mediaType ? { media_type: mediaType } : {}),
				...(num(year) != null ? { year: num(year) } : {}),
				...(num(minYear) != null ? { min_year: num(minYear) } : {}),
				...(num(maxYear) != null ? { max_year: num(maxYear) } : {}),
				...(minRating.trim() ? { min_rating: Number(minRating) } : {}),
				...(maxRating.trim() ? { max_rating: Number(maxRating) } : {}),
				...(unwatched ? { unwatched: true } : {}),
				sort_by: sortBy,
				sort_dir: sortDir,
				limit: 50,
				offset: 0,
			});
			const items = Array.isArray(res) ? res : (res?.results ?? res?.data ?? []);
			setResults(Array.isArray(items) ? items : []);
			setSearched(true);
		} catch (err) {
			setError(err instanceof Error ? err.message : "Advanced search failed");
		} finally {
			setLoading(false);
		}
	};

	return (
		<section aria-label="Advanced search" className="mt-6 max-w-4xl">
			<button
				type="button"
				onClick={() => setOpen((v) => !v)}
				data-testid="adv-search-toggle"
				className="text-xs font-bold uppercase tracking-widest text-slate-400 hover:text-amber transition-colors"
			>
				{open ? "Hide advanced filters" : "Show advanced filters"}
			</button>
			{open && (
				<form
					onSubmit={submit}
					className="mt-3 rounded-xl glass-panel border border-slate-600/50 p-4 grid sm:grid-cols-2 lg:grid-cols-3 gap-3"
				>
					<input
						data-testid="adv-search-title"
						value={title}
						onChange={(e) => setTitle(e.target.value)}
						placeholder="Title"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-genre"
						value={genre}
						onChange={(e) => setGenre(e.target.value)}
						placeholder="Genre"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-actor"
						value={actor}
						onChange={(e) => setActor(e.target.value)}
						placeholder="Actor"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-director"
						value={director}
						onChange={(e) => setDirector(e.target.value)}
						placeholder="Director"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-collection"
						value={collection}
						onChange={(e) => setCollection(e.target.value)}
						placeholder="Collection"
						className={inputCls}
					/>
					<select
						data-testid="adv-search-media-type"
						value={mediaType}
						onChange={(e) => setMediaType(e.target.value)}
						className={inputCls}
					>
						<option value="">Any type</option>
						<option value="movie">Movie</option>
						<option value="show">Show</option>
						<option value="episode">Episode</option>
						<option value="artist">Artist</option>
						<option value="album">Album</option>
					</select>
					<input
						data-testid="adv-search-year"
						value={year}
						onChange={(e) => setYear(e.target.value)}
						placeholder="Year"
						inputMode="numeric"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-min-year"
						value={minYear}
						onChange={(e) => setMinYear(e.target.value)}
						placeholder="Min year"
						inputMode="numeric"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-max-year"
						value={maxYear}
						onChange={(e) => setMaxYear(e.target.value)}
						placeholder="Max year"
						inputMode="numeric"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-min-rating"
						value={minRating}
						onChange={(e) => setMinRating(e.target.value)}
						placeholder="Min rating 0-10"
						inputMode="decimal"
						className={inputCls}
					/>
					<input
						data-testid="adv-search-max-rating"
						value={maxRating}
						onChange={(e) => setMaxRating(e.target.value)}
						placeholder="Max rating 0-10"
						inputMode="decimal"
						className={inputCls}
					/>
					<select
						data-testid="adv-search-sort-by"
						value={sortBy}
						onChange={(e) => setSortBy(e.target.value)}
						className={inputCls}
					>
						<option value="titleSort">Sort: title</option>
						<option value="year">Sort: year</option>
						<option value="rating">Sort: rating</option>
						<option value="addedAt">Sort: added</option>
					</select>
					<select
						data-testid="adv-search-sort-dir"
						value={sortDir}
						onChange={(e) => setSortDir(e.target.value)}
						className={inputCls}
					>
						<option value="asc">Asc</option>
						<option value="desc">Desc</option>
					</select>
					<label className="flex items-center gap-2 text-sm text-slate-300">
						<input
							type="checkbox"
							checked={unwatched}
							onChange={(e) => setUnwatched(e.target.checked)}
							data-testid="adv-search-unwatched"
						/>
						Unwatched only
					</label>
					<div className="sm:col-span-2 lg:col-span-3 flex items-center gap-3">
						<button
							type="submit"
							disabled={loading}
							data-testid="adv-search-submit"
							className="px-5 py-2 rounded-lg bg-amber text-slate-950 font-semibold hover:bg-amber/90 disabled:opacity-60"
						>
							{loading ? "Searching…" : "Run advanced search"}
						</button>
						{error && <span className="text-sm text-red-400">{error}</span>}
					</div>
				</form>
			)}
			{searched && (
				<div data-testid="adv-search-results" className="mt-4">
					<p className="text-xs text-slate-500 mb-2">
						{results.length} of {results.length} (advanced filters)
					</p>
					{results.length > 0 ? (
						<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
							{results.map((movie: unknown, i: number) => {
								const raw = movie as Record<string, unknown>;
								const m = {
									title: String(raw.title ?? raw.name ?? "Unknown"),
									ratingKey: raw.ratingKey != null ? String(raw.ratingKey) : undefined,
									id: raw.id != null ? String(raw.id) : undefined,
									key: raw.key != null ? String(raw.key) : undefined,
									year: typeof raw.year === "number" ? raw.year : undefined,
									thumb: typeof raw.thumb === "string" ? raw.thumb : undefined,
								};
								const key = String(m.ratingKey ?? m.id ?? m.key ?? i);
								return <MovieCard key={key} movie={m} onClick={() => {}} />;
							})}
						</div>
					) : (
						<p className="text-sm text-slate-500">No results for these filters.</p>
					)}
				</div>
			)}
		</section>
	);
}
