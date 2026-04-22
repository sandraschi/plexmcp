"use client";

import { MediaAiContextPanel } from "@/components/media/media-ai-context-panel";
import { ratingKeyFromItem } from "@/utils/plex-media-ui";
import { useState } from "react";
import MovieCard from "../components/MovieCard";
import MovieMetadataModal from "../components/MovieMetadataModal";
import { SearchForm } from "./search-form";

interface SearchClientProps {
	results: any[];
	query?: string;
	libraryId?: string;
	mode?: string;
	plexUrl?: string | null;
}

export default function SearchClient({
	results,
	query,
	libraryId,
	mode = "context",
	plexUrl,
}: SearchClientProps) {
	const [selectedMovie, setSelectedMovie] = useState<any | null>(null);
	const [aiContextRatingKey, setAiContextRatingKey] = useState<string | null>(null);

	const openAiFromMovie = (movie: Record<string, unknown>) => {
		const rk = ratingKeyFromItem(movie);
		if (rk) setAiContextRatingKey(rk);
	};

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-2 text-slate-100">Search</h1>
			<p className="text-slate-500 mb-6 font-medium tracking-tight">
				{mode === "context"
					? "Keyword search across Plex. Use Chat with RAG for semantic-style context."
					: "Deep dialogue search using neural embeddings. Finds exact lines and quotes."}
			</p>

			<SearchForm query={query} libraryId={libraryId} mode={mode as any} />

			{results.length > 0 ? (
				<div className="mt-8">
					{mode === "context" ? (
						<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
							{results.map((movie) => (
								<MovieCard
									key={movie.ratingKey || movie.id || movie.key}
									movie={movie}
									onClick={() => setSelectedMovie(movie)}
									onAiContext={() => openAiFromMovie(movie)}
								/>
							))}
						</div>
					) : (
						<div className="flex flex-col gap-4 max-w-4xl">
							{results.map((result, i) => (
								<DialogueResult key={i} result={result} />
							))}
						</div>
					)}
				</div>
			) : (
				query && (
					<div className="mt-12 text-center text-slate-500">
						<p>
							No results found for "{query}" in {mode} mode.
						</p>
					</div>
				)
			)}

			<MediaAiContextPanel
				ratingKey={aiContextRatingKey}
				onClose={() => setAiContextRatingKey(null)}
			/>
			{selectedMovie && (
				<MovieMetadataModal
					movie={selectedMovie}
					plexUrl={plexUrl}
					onClose={() => setSelectedMovie(null)}
					onOpenAiContext={() => openAiFromMovie(selectedMovie)}
				/>
			)}
		</div>
	);
}

function DialogueResult({ result }: { result: any }) {
	const { metadata, content } = result;

	// Extract dialogue from content formatted as "Media: Title\nTime: 00:00:00 - 00:00:00\nDialogue: text"
	const dialogueMatch = content?.match(/Dialogue: (.*)$/);
	const dialogue = dialogueMatch ? dialogueMatch[1] : content;

	const timeMatch = content?.match(/Time: (.*)\n/);
	const timestamp = timeMatch ? timeMatch[1] : null;

	return (
		<div className="glass-panel p-5 border-l-4 border-purple-500 hover:bg-slate-800/50 transition-colors group">
			<div className="flex justify-between items-start mb-3">
				<div className="flex flex-col">
					<span className="text-xs font-bold text-purple-400 uppercase tracking-widest">
						{metadata?.title || "Unknown Media"}
					</span>
					{timestamp && (
						<span className="text-[10px] text-slate-500 font-mono mt-0.5">{timestamp}</span>
					)}
				</div>
				<button className="text-[10px] font-bold text-slate-500 hover:text-white uppercase tracking-tighter border border-slate-700 px-2 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
					View Scene
				</button>
			</div>
			<p className="text-sm text-slate-200 leading-relaxed italic">"{dialogue}"</p>
		</div>
	);
}
