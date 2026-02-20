import React, { useState } from 'react';
import { XMarkIcon, PlayIcon } from '@heroicons/react/24/solid';
import { playMedia } from '../../utils/playback';

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

interface MovieMetadataModalProps {
    movie: Movie | null;
    onClose: () => void;
}

export default function MovieMetadataModal({ movie, onClose }: MovieMetadataModalProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!movie) return null;

    const handlePlay = async () => {
        setIsPlaying(true);
        setError(null);
        try {
            // Pass raw ratingKey or key? 
            // plex_media returns items with 'ratingKey' usually as the ID
            // but streaming.py expects 'media_key'. 
            // Usually media_key matches ratingKey in Plex tools logic.
            await playMedia(movie.ratingKey);
            // We could show a success message or close modal
            // For now, let's just show "Playing..." state
        } catch (err: any) {
            setError(err.message || 'Failed to start playback');
            setIsPlaying(false);
        }
    };

    const backdropUrl = movie.art ? `/image${movie.art}` : null;
    const posterUrl = movie.thumb ? `/image${movie.thumb}` : null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" onClick={onClose}>
            <div
                className="relative w-full max-w-4xl overflow-hidden rounded-2xl bg-slate-900 shadow-2xl ring-1 ring-white/10"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Backdrop Image */}
                {backdropUrl && (
                    <div className="absolute inset-0 h-64 opacity-20">
                        <img src={backdropUrl} alt="Backdrop" className="h-full w-full object-cover" />
                        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-900" />
                    </div>
                )}

                {/* Close Button */}
                <button
                    onClick={onClose}
                    title="Close"
                    aria-label="Close"
                    className="absolute top-4 right-4 z-10 rounded-full bg-black/50 p-2 text-white hover:bg-white/20 transition-colors"
                >
                    <XMarkIcon className="h-6 w-6" />
                </button>

                <div className="relative z-0 flex flex-col md:flex-row gap-6 p-6 md:p-8 mt-4">
                    {/* Poster */}
                    <div className="flex-shrink-0 w-32 md:w-64 mx-auto md:mx-0">
                        {posterUrl ? (
                            <img src={posterUrl} alt={movie.title} className="w-full rounded-lg shadow-xl" />
                        ) : (
                            <div className="w-full aspect-[2/3] bg-slate-800 rounded-lg flex items-center justify-center text-slate-500">
                                No Poster
                            </div>
                        )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 flex flex-col gap-4 text-slate-100">
                        <div>
                            <h2 className="text-3xl font-bold">{movie.title}</h2>
                            <div className="flex items-center gap-3 text-sm text-slate-400 mt-1">
                                {movie.year && <span>{movie.year}</span>}
                                {movie.duration && <span>{Math.round(movie.duration / 60000)} min</span>}
                                {movie.type && <span className="uppercase text-xs font-bold bg-slate-800 px-2 py-0.5 rounded">{movie.type}</span>}
                            </div>
                        </div>

                        {movie.tagline && (
                            <p className="text-lg italic text-slate-300 font-light">"{movie.tagline}"</p>
                        )}

                        <div className="prose prose-invert max-w-none">
                            <p>{movie.summary || "No summary available."}</p>
                        </div>

                        <div className="mt-auto pt-6 flex flex-col gap-2">
                            {error && (
                                <div className="text-red-400 text-sm bg-red-900/20 p-2 rounded">
                                    {error}
                                </div>
                            )}
                            <button
                                onClick={handlePlay}
                                disabled={isPlaying}
                                className={`
                            flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold text-lg transition-all
                            ${isPlaying
                                        ? 'bg-amber-600 cursor-wait opacity-80'
                                        : 'bg-amber-500 hover:bg-amber-400 hover:scale-105 active:scale-95 text-black shadow-lg shadow-amber-500/20'
                                    }
                        `}
                            >
                                <PlayIcon className="h-6 w-6" />
                                {isPlaying ? 'Starting Playback...' : 'Play on Client'}
                            </button>
                            <p className="text-xs text-center text-slate-500">
                                Plays on the active Plex client (or first available).
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
