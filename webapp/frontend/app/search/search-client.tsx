"use client";

import { useState } from "react";
import MovieCard from "../components/MovieCard";
import MovieMetadataModal from "../components/MovieMetadataModal";
import { SearchForm } from "./search-form";

interface SearchClientProps {
    movies: any[];
    query?: string;
    libraryId?: string;
}

export default function SearchClient({ movies, query, libraryId }: SearchClientProps) {
    const [selectedMovie, setSelectedMovie] = useState<any | null>(null);

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-3xl font-bold mb-2 text-slate-100">Search</h1>
            <p className="text-slate-500 mb-6">Keyword search across Plex. Use Chat with RAG for semantic-style context.</p>

            <SearchForm query={query} libraryId={libraryId} />

            {movies.length > 0 ? (
                <div className="mt-8 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {movies.map((movie) => (
                        <MovieCard
                            key={movie.ratingKey || movie.key}
                            movie={movie}
                            onClick={() => setSelectedMovie(movie)}
                        />
                    ))}
                </div>
            ) : (
                query && (
                    <div className="mt-12 text-center text-slate-500">
                        <p>No results found for "{query}".</p>
                    </div>
                )
            )}

            {selectedMovie && (
                <MovieMetadataModal
                    movie={selectedMovie}
                    onClose={() => setSelectedMovie(null)}
                />
            )}
        </div>
    );
}
