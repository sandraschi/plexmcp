"use client";

import { ReindexProgressPanel } from "@/components/rag/reindex-progress";
import {
	getLlmModels,
	getRagSyncStatus,
	getSettings,
	startRagSync,
	updateSettings,
} from "@/utils/api";
import type { RagSyncProgress } from "@/utils/api";
import { useCallback, useEffect, useRef, useState } from "react";

const DEFAULT_MOVIES_LIBRARY_KEY = "plex-webapp-default-movies-library";
const DEFAULT_LLM_MODEL_KEY = "plex-webapp-default-llm-model";

interface SettingsClientProps {
	settings: {
		plex_token_set?: boolean;
		plex_token?: string | null;
		plex_url?: string | null;
		llm_provider?: string | null;
		llm_base_url?: string | null;
		llm_api_key_set?: boolean;
		llm_api_key?: string | null;
		radarr_url?: string | null;
		radarr_api_key_set?: boolean;
		radarr_api_key?: string | null;
		sonarr_url?: string | null;
		sonarr_api_key_set?: boolean;
		sonarr_api_key?: string | null;
		lidarr_url?: string | null;
		lidarr_api_key_set?: boolean;
		lidarr_api_key?: string | null;
		tmdb_api_key_set?: boolean;
		tmdb_api_key?: string | null;
		api_version?: string;
	};
}

export function SettingsClient({ settings }: SettingsClientProps) {
	const [plexToken, setPlexToken] = useState("");
	const [plexUrl, setPlexUrl] = useState("");
	const [llmProvider, setLlmProvider] = useState("ollama");
	const [llmBaseUrl, setLlmBaseUrl] = useState("");
	const [llmApiKey, setLlmApiKey] = useState("");
	const [radarrUrl, setRadarrUrl] = useState("");
	const [radarrApiKey, setRadarrApiKey] = useState("");
	const [sonarrUrl, setSonarrUrl] = useState("");
	const [sonarrApiKey, setSonarrApiKey] = useState("");
	const [lidarrUrl, setLidarrUrl] = useState("");
	const [lidarrApiKey, setLidarrApiKey] = useState("");
	const [tmdbApiKey, setTmdbApiKey] = useState("");
	const [defaultLlmModel, setDefaultLlmModel] = useState("");
	const [defaultMoviesLibrary, setDefaultMoviesLibrary] = useState("");
	const [models, setModels] = useState<string[]>([]);
	const [modelError, setModelError] = useState<string | null>(null);
	const [saving, setSaving] = useState(false);
	const [message, setMessage] = useState<{
		type: "ok" | "err";
		text: string;
	} | null>(null);
	const [ragReindexing, setRagReindexing] = useState(false);
	const [ragReindexResult, setRagReindexResult] = useState<{
		count: number;
		error?: string;
	} | null>(null);
	const [ragProgress, setRagProgress] = useState<RagSyncProgress | null>(null);
	const ragPollRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const stopRagPoll = useCallback(() => {
		if (ragPollRef.current != null) {
			clearInterval(ragPollRef.current);
			ragPollRef.current = null;
		}
	}, []);

	// Elicit models from the LLM endpoint
	const loadModels = useCallback(async (provider: string, baseUrl: string) => {
		setModelError(null);
		try {
			const d = await getLlmModels({
				provider,
				base_url: baseUrl || undefined,
			});
			setModels(d.models ?? []);
			if (!d.models?.length && d.error) setModelError(d.error);
		} catch (e) {
			setModels([]);
			setModelError(e instanceof Error ? e.message : "Failed to fetch models");
		}
	}, []);

	useEffect(() => {
		const p = settings.llm_provider ?? "ollama";
		const u = settings.llm_base_url ?? "";
		setPlexUrl(settings.plex_url ?? "");
		setLlmProvider(p);
		setLlmBaseUrl(u);
		if (typeof window !== "undefined") {
			setDefaultMoviesLibrary(localStorage.getItem(DEFAULT_MOVIES_LIBRARY_KEY) ?? "");
			setDefaultLlmModel(localStorage.getItem(DEFAULT_LLM_MODEL_KEY) ?? "");
		}
		void loadModels(p, u);
	}, [settings, loadModels]);

	// Re-elicit when provider or base_url changes (500ms debounce)
	useEffect(() => {
		const timer = setTimeout(() => void loadModels(llmProvider, llmBaseUrl), 500);
		return () => clearTimeout(timer);
	}, [llmProvider, llmBaseUrl, loadModels]);

	useEffect(() => {
		return () => stopRagPoll();
	}, [stopRagPoll]);

	const handleRagReindex = async () => {
		setRagReindexing(true);
		setRagReindexResult(null);
		setRagProgress({ phase: "starting", message: "Starting reindex..." });
		stopRagPoll();

		try {
			const started = await startRagSync();
			if (!started.success && !started.already_running) {
				const err = started.error ?? "Could not start reindex";
				setRagProgress({ phase: "error", message: err });
				setRagReindexResult({ count: 0, error: err });
				setRagReindexing(false);
				return;
			}
			if (started.already_running) {
				setRagProgress((prev) => ({
					...prev,
					phase: "processing_library",
					message: "A reindex is already running — showing its progress.",
				}));
			}

			const tick = async () => {
				try {
					const p = await getRagSyncStatus();
					setRagProgress(p);
					if (p.phase === "complete") {
						stopRagPoll();
						setRagReindexResult({ count: p.indexed_count ?? 0 });
						setRagReindexing(false);
					} else if (p.phase === "error") {
						stopRagPoll();
						setRagReindexResult({
							count: 0,
							error: p.message ?? "Reindex failed",
						});
						setRagReindexing(false);
					}
				} catch (e) {
					stopRagPoll();
					const msg = e instanceof Error ? e.message : "Status poll failed";
					setRagProgress({ phase: "error", message: msg });
					setRagReindexResult({ count: 0, error: msg });
					setRagReindexing(false);
				}
			};

			await tick();
			ragPollRef.current = setInterval(tick, 450);
		} catch (e) {
			const msg = e instanceof Error ? e.message : "Request failed";
			setRagProgress({ phase: "error", message: msg });
			setRagReindexResult({ count: 0, error: msg });
			setRagReindexing(false);
		}
	};

	const handleSave = async () => {
		setSaving(true);
		setMessage(null);
		try {
			const body: Record<string, string> = {};
			if (plexToken.trim()) body.plex_token = plexToken.trim();
			if (plexUrl.trim()) body.plex_url = plexUrl.trim();
			if (llmProvider) body.llm_provider = llmProvider;
			if (llmBaseUrl.trim()) body.llm_base_url = llmBaseUrl.trim();
			if (llmApiKey.trim()) body.llm_api_key = llmApiKey.trim();
			if (radarrUrl.trim()) body.radarr_url = radarrUrl.trim();
			if (radarrApiKey.trim()) body.radarr_api_key = radarrApiKey.trim();
			if (sonarrUrl.trim()) body.sonarr_url = sonarrUrl.trim();
			if (sonarrApiKey.trim()) body.sonarr_api_key = sonarrApiKey.trim();
			if (lidarrUrl.trim()) body.lidarr_url = lidarrUrl.trim();
			if (lidarrApiKey.trim()) body.lidarr_api_key = lidarrApiKey.trim();
			if (tmdbApiKey.trim()) body.tmdb_api_key = tmdbApiKey.trim();
			await updateSettings(body);
			if (typeof window !== "undefined") {
				if (defaultMoviesLibrary)
					localStorage.setItem(DEFAULT_MOVIES_LIBRARY_KEY, defaultMoviesLibrary);
				else localStorage.removeItem(DEFAULT_MOVIES_LIBRARY_KEY);
				if (defaultLlmModel) localStorage.setItem(DEFAULT_LLM_MODEL_KEY, defaultLlmModel);
				else localStorage.removeItem(DEFAULT_LLM_MODEL_KEY);
			}
			setMessage({ type: "ok", text: "Settings saved." });
			if (plexToken.trim()) setPlexToken("");
			if (llmApiKey.trim()) setLlmApiKey("");
			if (radarrApiKey.trim()) setRadarrApiKey("");
			if (sonarrApiKey.trim()) setSonarrApiKey("");
			if (lidarrApiKey.trim()) setLidarrApiKey("");
			if (tmdbApiKey.trim()) setTmdbApiKey("");
		} catch (e) {
			setMessage({
				type: "err",
				text: e instanceof Error ? e.message : "Save failed",
			});
		} finally {
			setSaving(false);
		}
	};

	return (
		<div className="space-y-8">
			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-4">Plex</h2>
				<div className="space-y-4">
					<div>
						<label className="block text-sm text-slate-400 mb-1">API key (X-Plex-Token)</label>
						<input
							type="password"
							value={plexToken}
							onChange={(e) => setPlexToken(e.target.value)}
							placeholder={
								settings.plex_token_set ? "Leave blank to keep current" : "Your Plex token"
							}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
					<div>
						<label className="block text-sm text-slate-400 mb-1">Plex URL</label>
						<input
							type="url"
							value={plexUrl}
							onChange={(e) => setPlexUrl(e.target.value)}
							placeholder="http://localhost:32400"
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
				</div>
			</section>

			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-2">TMDB (AI context)</h2>
				<p className="text-xs text-slate-500 mb-4">
					Optional v3 API key for movie/TV match, poster, and overview in the AI context panel.{" "}
					<a
						href="https://www.themoviedb.org/settings/api"
						target="_blank"
						rel="noopener noreferrer"
						className="text-amber/90 underline underline-offset-2"
					>
						Get a key
					</a>
				</p>
				<div>
					<label className="block text-sm text-slate-400 mb-1">TMDB API key</label>
					<input
						type="password"
						value={tmdbApiKey}
						onChange={(e) => setTmdbApiKey(e.target.value)}
						placeholder={
							settings.tmdb_api_key_set
								? "Leave blank to keep current"
								: "Paste API read access token"
						}
						className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
					/>
				</div>
			</section>

			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-4">LLM</h2>
				<div className="space-y-4">
					<div>
						<label className="block text-sm text-slate-400 mb-1">Provider</label>
						<select
							value={llmProvider}
							onChange={(e) => setLlmProvider(e.target.value)}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm"
						>
							<option value="ollama">Ollama</option>
							<option value="lmstudio">LM Studio</option>
							<option value="openai">OpenAI-compatible</option>
						</select>
					</div>
					<div>
						<label className="block text-sm text-slate-400 mb-1">Base URL</label>
						<input
							type="url"
							value={llmBaseUrl}
							onChange={(e) => setLlmBaseUrl(e.target.value)}
							placeholder="http://127.0.0.1:11434"
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
					<div>
						<label className="block text-sm text-slate-400 mb-1">API key (optional)</label>
						<input
							type="password"
							value={llmApiKey}
							onChange={(e) => setLlmApiKey(e.target.value)}
							placeholder={
								settings.llm_api_key_set ? "Leave blank to keep current" : "For OpenAI-compatible"
							}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
					<div>
						<label className="block text-sm text-slate-400 mb-1">
							Default model (for Chat, saved in browser)
						</label>
						<select
							value={defaultLlmModel}
							onChange={(e) => setDefaultLlmModel(e.target.value)}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm"
						>
							<option value="">Select after loading...</option>
							{models.map((m) => (
								<option key={m} value={m}>
									{m}
								</option>
							))}
						</select>
						{modelError && <p className="text-red-400 text-xs mt-1">{modelError}</p>}
						<p className="text-xs text-slate-500 mt-1">
							Fetched from LLM endpoint
							{models.length > 0 ? ` (${models.length} available)` : ""}.{" "}
							<button
								type="button"
								onClick={() => void loadModels(llmProvider, llmBaseUrl)}
								className="text-amber/90 hover:text-amber underline underline-offset-2"
							>
								Refresh
							</button>
						</p>
					</div>
				</div>
			</section>

			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-2">*arr stack (optional)</h2>
				<p className="text-sm text-slate-500 mb-4">
					Base URL and API key for each app (in Radarr/Sonarr/Lidarr: Settings → General →
					Security). These usually run in Docker as part of a media stack; use the URL that works
					from this machine (e.g. <code className="text-amber text-xs">http://127.0.0.1:7878</code>{" "}
					if published on the host, or your Traefik hostname). Read-only status for the Overview
					page and MCP <code className="text-amber text-xs">arr_stack</code>.
				</p>
				<div className="space-y-6">
					<div className="space-y-2">
						<h3 className="text-sm font-medium text-slate-300">Radarr</h3>
						<input
							type="url"
							value={radarrUrl}
							onChange={(e) => setRadarrUrl(e.target.value)}
							placeholder="http://127.0.0.1:7878 or https://radarr.example.com"
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
						<input
							type="password"
							value={radarrApiKey}
							onChange={(e) => setRadarrApiKey(e.target.value)}
							placeholder={
								settings.radarr_api_key_set ? "Leave blank to keep current API key" : "API key"
							}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
					<div className="space-y-2">
						<h3 className="text-sm font-medium text-slate-300">Sonarr</h3>
						<input
							type="url"
							value={sonarrUrl}
							onChange={(e) => setSonarrUrl(e.target.value)}
							placeholder="http://127.0.0.1:8989"
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
						<input
							type="password"
							value={sonarrApiKey}
							onChange={(e) => setSonarrApiKey(e.target.value)}
							placeholder={
								settings.sonarr_api_key_set ? "Leave blank to keep current API key" : "API key"
							}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
					<div className="space-y-2">
						<h3 className="text-sm font-medium text-slate-300">Lidarr</h3>
						<input
							type="url"
							value={lidarrUrl}
							onChange={(e) => setLidarrUrl(e.target.value)}
							placeholder="http://127.0.0.1:8686 or https://lidarr.example.com"
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
						<input
							type="password"
							value={lidarrApiKey}
							onChange={(e) => setLidarrApiKey(e.target.value)}
							placeholder={
								settings.lidarr_api_key_set ? "Leave blank to keep current API key" : "API key"
							}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
				</div>
			</section>

			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-4">RAG / Indexing</h2>
				<p className="text-sm text-slate-400 mb-3">
					Sync Plex metadata into the semantic search index. Use after adding libraries or when
					search is stale. First run may download the embedding model.
				</p>
				<button
					type="button"
					onClick={handleRagReindex}
					disabled={ragReindexing}
					className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 font-medium hover:bg-slate-600 disabled:opacity-50 border border-slate-600/50"
				>
					{ragReindexing ? "Reindexing..." : "Reindex metadata"}
				</button>
				<ReindexProgressPanel progress={ragProgress} />
				{ragReindexResult && !ragReindexing && (
					<p className="text-sm mt-3 text-slate-400">
						{ragReindexResult.error
							? `Error: ${ragReindexResult.error}`
							: `Done. Indexed ${ragReindexResult.count} item(s).`}
					</p>
				)}
			</section>

			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-4">Client preferences</h2>
				<div className="space-y-2">
					<label className="block text-sm text-slate-400">
						Default movies library (saved in browser)
					</label>
					<input
						type="text"
						value={defaultMoviesLibrary}
						onChange={(e) => setDefaultMoviesLibrary(e.target.value)}
						placeholder="Library key or leave empty"
						className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
					/>
				</div>
			</section>

			{message && (
				<p className={message.type === "ok" ? "text-green-400 text-sm" : "text-amber text-sm"}>
					{message.text}
				</p>
			)}
			<button
				type="button"
				onClick={handleSave}
				disabled={saving}
				className="px-6 py-3 rounded-xl bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50"
			>
				{saving ? "Saving..." : "Save settings"}
			</button>
		</div>
	);
}
