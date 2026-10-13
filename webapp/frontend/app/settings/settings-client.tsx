"use client";

import { ReindexProgressPanel } from "@/components/rag/reindex-progress";
import { DiagnosticsPanel } from "@/components/settings/DiagnosticsPanel";
import { LlmOnboardingCard } from "@/components/settings/LlmOnboardingCard";
import { VramPanel } from "@/components/settings/VramPanel";
import {
	createPlexPin,
	deleteLlmProviderKey,
	getLlmModels,
	getLlmProviders,
	getRagSyncStatus,
	getSettings,
	pollPlexPin,
	saveLlmProviderKey,
	startRagSync,
	testPlexConnection,
	updateSettings,
} from "@/utils/api";
import type { LlmProviderInfo, RagSyncProgress } from "@/utils/api";
import { useCallback, useEffect, useRef, useState } from "react";

const PIN_POLL_MS = 2000;
const PIN_TIMEOUT_MS = 5 * 60 * 1000;

/** Providers whose API key is saved per-provider to the backend keystore
 * (POST /api/llm/keys/{provider}) rather than the legacy flat llm_api_key
 * field. Ollama/LM Studio need no key; OpenAI keeps the legacy flat field
 * for backward compatibility with existing setups. */
const KEYSTORE_CLOUD_PROVIDERS = ["anthropic", "deepseek", "openrouter"];

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
	const [llmProviders, setLlmProviders] = useState<LlmProviderInfo[]>([]);
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
	const [plexTokenSet, setPlexTokenSet] = useState(settings.plex_token_set ?? false);
	const [plexTesting, setPlexTesting] = useState(false);
	const [plexTestResult, setPlexTestResult] = useState<{
		type: "ok" | "err";
		text: string;
	} | null>(null);
	const [plexPinFlow, setPlexPinFlow] = useState<{
		status: "idle" | "waiting" | "success" | "error";
		message?: string;
	}>({ status: "idle" });
	const plexPinPollRef = useRef<ReturnType<typeof setInterval> | null>(null);
	const plexPinTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

	const stopRagPoll = useCallback(() => {
		if (ragPollRef.current != null) {
			clearInterval(ragPollRef.current);
			ragPollRef.current = null;
		}
	}, []);

	const stopPlexPinPoll = useCallback(() => {
		if (plexPinPollRef.current != null) {
			clearInterval(plexPinPollRef.current);
			plexPinPollRef.current = null;
		}
		if (plexPinTimeoutRef.current != null) {
			clearTimeout(plexPinTimeoutRef.current);
			plexPinTimeoutRef.current = null;
		}
	}, []);

	const handleProviderChange = (nextProvider: string) => {
		setLlmProvider(nextProvider);
		setLlmApiKey("");
		// A stale local base_url would otherwise leak into a cloud provider's
		// model/chat requests and get misread by the legacy host-sniffing
		// fallback instead of engaging the provider registry.
		if (nextProvider === "openai" || KEYSTORE_CLOUD_PROVIDERS.includes(nextProvider)) {
			setLlmBaseUrl("");
		}
	};

	const loadProviders = useCallback(async () => {
		try {
			const d = await getLlmProviders();
			setLlmProviders(d.providers);
		} catch {
			setLlmProviders([]);
		}
	}, []);

	useEffect(() => {
		void loadProviders();
	}, [loadProviders]);

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

	useEffect(() => {
		return () => stopPlexPinPoll();
	}, [stopPlexPinPoll]);

	const handleTestPlexConnection = async () => {
		setPlexTesting(true);
		setPlexTestResult(null);
		try {
			const result = await testPlexConnection({
				plex_url: plexUrl.trim() || undefined,
				plex_token: plexToken.trim() || undefined,
			});
			setPlexTestResult({ type: result.success ? "ok" : "err", text: result.message });
		} catch (e) {
			setPlexTestResult({
				type: "err",
				text: e instanceof Error ? e.message : "Test failed",
			});
		} finally {
			setPlexTesting(false);
		}
	};

	const handleGetNewPlexToken = async () => {
		stopPlexPinPoll();
		setPlexTestResult(null);
		setPlexPinFlow({ status: "waiting", message: "Requesting a code from plex.tv..." });
		try {
			const pin = await createPlexPin();
			if (!pin.success || !pin.data) {
				setPlexPinFlow({ status: "error", message: pin.message });
				return;
			}
			const { pin_id, client_id, auth_url } = pin.data;
			window.open(auth_url, "_blank", "noopener,noreferrer");
			setPlexPinFlow({
				status: "waiting",
				message: "Sign in and approve access in the tab that just opened...",
			});

			plexPinPollRef.current = setInterval(async () => {
				try {
					const poll = await pollPlexPin(pin_id, client_id);
					if (poll.success && poll.data?.authorized) {
						stopPlexPinPoll();
						setPlexPinFlow({ status: "success", message: "New token saved." });
						setPlexTokenSet(true);
						setPlexToken("");
					} else if (!poll.success) {
						stopPlexPinPoll();
						setPlexPinFlow({ status: "error", message: poll.message });
					}
				} catch (e) {
					stopPlexPinPoll();
					setPlexPinFlow({
						status: "error",
						message: e instanceof Error ? e.message : "Could not check authorization status",
					});
				}
			}, PIN_POLL_MS);

			plexPinTimeoutRef.current = setTimeout(() => {
				stopPlexPinPoll();
				setPlexPinFlow((prev) =>
					prev.status === "waiting"
						? { status: "error", message: "Timed out waiting for authorization. Try again." }
						: prev,
				);
			}, PIN_TIMEOUT_MS);
		} catch (e) {
			setPlexPinFlow({
				status: "error",
				message: e instanceof Error ? e.message : "Could not start Plex sign-in",
			});
		}
	};

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
			// Cloud providers beyond OpenAI save to the per-provider keystore
			// (POST /api/llm/keys/{provider}) instead of the legacy flat
			// llm_api_key field, so multiple cloud keys can coexist.
			if (llmApiKey.trim() && KEYSTORE_CLOUD_PROVIDERS.includes(llmProvider)) {
				await saveLlmProviderKey(llmProvider, llmApiKey.trim());
			} else if (llmApiKey.trim()) {
				body.llm_api_key = llmApiKey.trim();
			}
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
			if (plexToken.trim()) {
				setPlexToken("");
				setPlexTokenSet(true);
			}
			if (llmApiKey.trim()) {
				setLlmApiKey("");
				void loadProviders();
			}
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
			<DiagnosticsPanel />

			<section className="rounded-xl glass-panel border border-slate-600/50 p-6">
				<h2 className="text-lg font-semibold text-amber mb-4">Plex</h2>
				<div className="space-y-4">
					<div>
						<label className="block text-sm text-slate-400 mb-1">API key (X-Plex-Token)</label>
						<input
							type="password"
							value={plexToken}
							onChange={(e) => setPlexToken(e.target.value)}
							placeholder={plexTokenSet ? "Leave blank to keep current" : "Your Plex token"}
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
					<div className="flex flex-wrap items-center gap-3">
						<button
							type="button"
							onClick={handleTestPlexConnection}
							disabled={plexTesting}
							data-testid="plex-test-connection"
							className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm font-medium hover:bg-slate-600 disabled:opacity-50 border border-slate-600/50"
						>
							{plexTesting ? "Testing..." : "Test connection"}
						</button>
						<button
							type="button"
							onClick={handleGetNewPlexToken}
							disabled={plexPinFlow.status === "waiting"}
							data-testid="plex-get-new-token"
							className="px-4 py-2 rounded-lg bg-slate-700 text-slate-200 text-sm font-medium hover:bg-slate-600 disabled:opacity-50 border border-slate-600/50"
						>
							{plexPinFlow.status === "waiting" ? "Waiting for approval..." : "Get a new token"}
						</button>
						{plexTokenSet && plexPinFlow.status !== "waiting" && (
							<span className="text-xs text-slate-500">A token is currently saved.</span>
						)}
					</div>
					{plexTestResult && (
						<p
							className={
								plexTestResult.type === "ok" ? "text-green-400 text-sm" : "text-amber text-sm"
							}
						>
							{plexTestResult.text}
						</p>
					)}
					{plexPinFlow.status !== "idle" && (
						<p
							className={
								plexPinFlow.status === "error"
									? "text-amber text-sm"
									: plexPinFlow.status === "success"
										? "text-green-400 text-sm"
										: "text-slate-400 text-sm"
							}
						>
							{plexPinFlow.message}
						</p>
					)}
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
				<LlmOnboardingCard />
				<div className="space-y-4">
					<div>
						<label className="block text-sm text-slate-400 mb-1">Provider</label>
						<select
							value={llmProvider}
							onChange={(e) => handleProviderChange(e.target.value)}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm"
						>
							<optgroup label="Local (needs a running engine)">
								<option value="ollama">Ollama</option>
								<option value="lmstudio">LM Studio</option>
								<option value="vllm">vLLM</option>
							</optgroup>
							<optgroup label="Cloud (no GPU required)">
								<option value="openai">OpenAI-compatible</option>
								<option value="anthropic">Anthropic</option>
								<option value="deepseek">DeepSeek</option>
								<option value="openrouter">OpenRouter</option>
							</optgroup>
						</select>
						{(() => {
							const info = llmProviders.find((p) => p.id === llmProvider);
							if (!info) return null;
							return (
								<p className="text-xs text-slate-500 mt-1">
									{info.kind === "cloud"
										? info.configured
											? "API key configured."
											: "No API key configured yet - paste one below."
										: "Local engine - no API key needed, just make sure it's running."}
								</p>
							);
						})()}
					</div>
					{!KEYSTORE_CLOUD_PROVIDERS.includes(llmProvider) && (
						<div>
							<label className="block text-sm text-slate-400 mb-1">
								{llmProvider === "openai" ? "Base URL (optional override)" : "Base URL"}
							</label>
							<input
								type="url"
								value={llmBaseUrl}
								onChange={(e) => setLlmBaseUrl(e.target.value)}
								placeholder="http://127.0.0.1:11434"
								className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
							/>
						</div>
					)}
					<div>
						<div className="flex items-center justify-between mb-1">
							<label className="block text-sm text-slate-400">
								{llmProviders.find((p) => p.id === llmProvider)?.kind === "cloud"
									? "API key"
									: "API key (optional)"}
							</label>
							{KEYSTORE_CLOUD_PROVIDERS.includes(llmProvider) &&
								llmProviders.find((p) => p.id === llmProvider)?.configured && (
									<button
										type="button"
										data-testid={`llm-key-delete-${llmProvider}`}
										onClick={() =>
											void (async () => {
												try {
													await deleteLlmProviderKey(llmProvider);
													setMessage({ type: "ok", text: "API key removed." });
													void loadProviders();
												} catch (e) {
													setMessage({
														type: "err",
														text: e instanceof Error ? e.message : "Delete failed",
													});
												}
											})()
										}
										className="text-xs text-red-400 hover:text-red-300 underline underline-offset-2"
									>
										Remove saved key
									</button>
								)}
						</div>
						<input
							type="password"
							value={llmApiKey}
							onChange={(e) => setLlmApiKey(e.target.value)}
							placeholder={
								llmProviders.find((p) => p.id === llmProvider)?.configured
									? "Leave blank to keep current"
									: settings.llm_api_key_set
										? "Leave blank to keep current"
										: "Paste your API key"
							}
							className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
						/>
					</div>
					<VramPanel />
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
