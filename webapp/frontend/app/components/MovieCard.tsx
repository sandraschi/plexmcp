import { plexImageUrl } from "@/utils/plex-media-ui";
import { PlayIcon } from "@heroicons/react/24/solid";
import React from "react";

interface Movie {
	title: string;
	year?: number;
	thumb?: string;
	art?: string;
	ratingKey?: string;
	id?: string;
	key?: string;
	summary?: string;
	tagline?: string;
	duration?: number;
	type?: string;
}

interface MovieCardProps {
	movie: Movie;
	onClick: (movie: Movie) => void;
	/** Wikipedia / TMDB / LLM context panel (rating key from movie). */
	onAiContext?: (movie: Movie) => void;
}

export default function MovieCard({ movie, onClick, onAiContext }: MovieCardProps) {
	const imageUrl = plexImageUrl(movie.thumb) ?? "/placeholder-movie.png";

	const rk = movie.ratingKey ?? movie.id;

	return (
		<div
			className="group relative flex flex-col gap-2 cursor-pointer transition-transform hover:scale-105"
			onClick={() => onClick(movie)}
		>
			<div className="relative aspect-[2/3] w-full overflow-hidden rounded-xl bg-slate-800 shadow-lg">
				{movie.thumb ? (
					<img
						src={imageUrl}
						alt={movie.title}
						className="h-full w-full object-cover transition-opacity group-hover:opacity-80"
						loading="lazy"
						onError={(e) => {
							(e.target as HTMLImageElement).src =
								"https://via.placeholder.com/300x450?text=No+Poster";
						}}
					/>
				) : (
					<div className="flex h-full items-center justify-center text-slate-500">No Poster</div>
				)}

				<div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
					<PlayIcon className="w-12 h-12 text-white drop-shadow-lg" />
				</div>
				{onAiContext && rk ? (
					<button
						type="button"
						className="absolute bottom-2 right-2 z-10 px-2 py-1 rounded-md text-[10px] font-semibold bg-slate-950/90 text-purple-200 border border-purple-400/50 hover:bg-slate-900 shadow-md"
						onClick={(e) => {
							e.stopPropagation();
							onAiContext(movie);
						}}
					>
						AI context
					</button>
				) : null}
			</div>

			<div className="flex flex-col">
				<h3 className="text-sm font-semibold text-slate-100 truncate" title={movie.title}>
					{movie.title}
				</h3>
				{movie.year && <span className="text-xs text-slate-400">{movie.year}</span>}
			</div>
		</div>
	);
}
