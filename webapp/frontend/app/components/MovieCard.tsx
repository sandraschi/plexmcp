import React from 'react';
import { PlayIcon } from '@heroicons/react/24/solid';

interface Movie {
    title: string;
    year?: number;
    thumb?: string;
    art?: string;
    ratingKey: string;
    key?: string;
    summary?: string;
    tagline?: string;
    duration?: number;
    type?: string;
}

interface MovieCardProps {
    movie: Movie;
    onClick: (movie: Movie) => void;
}

export default function MovieCard({ movie, onClick }: MovieCardProps) {
    // Construct image URL using our backend proxy
    // If thumb starts with /, we append it to /image API
    // e.g. /image/library/metadata/123/thumb/123
    const imageUrl = movie.thumb ? `/image${movie.thumb}` : '/placeholder-movie.png';

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
                            (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x450?text=No+Poster';
                        }}
                    />
                ) : (
                    <div className="flex h-full items-center justify-center text-slate-500">
                        No Poster
                    </div>
                )}

                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                    <PlayIcon className="w-12 h-12 text-white drop-shadow-lg" />
                </div>
            </div>

            <div className="flex flex-col">
                <h3 className="text-sm font-semibold text-slate-100 truncate" title={movie.title}>
                    {movie.title}
                </h3>
                {movie.year && (
                    <span className="text-xs text-slate-400">{movie.year}</span>
                )}
            </div>
        </div>
    );
}
