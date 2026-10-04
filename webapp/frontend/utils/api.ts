/** Empty in dev (Next rewrites); direct backend URL in production / Tauri. */
export const API_BASE = process.env.NODE_ENV === "development" ? "" : "http://127.0.0.1:10740";

export function getBaseUrl(): string {
	return API_BASE;
}

export async function getServerStatus() {
	const res = await fetch(`${getBaseUrl()}/api/server/status`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function getServerInfo() {
	const res = await fetch(`${getBaseUrl()}/api/server/info`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function checkBackendHealth(): Promise<boolean> {
	try {
		const res = await fetch(`${getBaseUrl()}/health`, { cache: "no-store" });
		return res.ok;
	} catch {
		return false;
	}
}

export async function listLibraries() {
	const res = await fetch(`${getBaseUrl()}/api/libraries/`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function search(params?: {
	query?: string;
	library_id?: string;
	limit?: number;
}) {
	const sp = new URLSearchParams();
	if (params?.query) sp.set("query", params.query);
	if (params?.library_id) sp.set("library_id", params.library_id);
	if (params?.limit) sp.set("limit", params.limit.toString());
	const res = await fetch(`${getBaseUrl()}/api/search/?${sp}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function getSystemStatus() {
	const res = await fetch(`${getBaseUrl()}/api/system/status`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type ArrServiceStatus = {
	name: string;
	configured: boolean;
	reachable: boolean;
	version: string | null;
	queue_count: number | null;
	error: string | null;
};

export type ArrStackResponse = {
	success: boolean;
	any_configured: boolean;
	radarr: ArrServiceStatus;
	sonarr: ArrServiceStatus;
	lidarr: ArrServiceStatus;
	hint?: string;
};

/** Radarr / Sonarr / Lidarr reachability (requires URLs + API keys in Settings or .env). */
export async function getArrStackStatus(): Promise<ArrStackResponse> {
	const res = await fetch(`${getBaseUrl()}/api/arr/status`, {
		cache: "no-store",
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function getLogs(params?: {
	tail?: number;
	filter?: string;
	level?: string;
}) {
	const sp = new URLSearchParams();
	if (params?.tail != null) sp.set("tail", String(params.tail));
	if (params?.filter) sp.set("filter", params.filter);
	if (params?.level) sp.set("level", params.level);
	const res = await fetch(`${getBaseUrl()}/api/logs?${sp}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function getHelp(level?: string) {
	const sp = level ? `?level=${encodeURIComponent(level)}` : "";
	const res = await fetch(`${getBaseUrl()}/api/help${sp}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function getMovies(params?: {
	library_id?: string;
	limit?: number;
	offset?: number;
}) {
	const sp = new URLSearchParams();
	if (params?.library_id) sp.set("library_id", params.library_id);
	if (params?.limit != null) sp.set("limit", String(params.limit));
	if (params?.offset != null) sp.set("offset", String(params.offset));
	const res = await fetch(`${getBaseUrl()}/api/movies?${sp}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Full metadata for one item (genres, cast, technical streams, etc.). */
export async function getMediaDetail(
	ratingKey: string,
): Promise<{ success: boolean; data: Record<string, unknown> }> {
	const res = await fetch(`${getBaseUrl()}/api/media/${encodeURIComponent(ratingKey)}`);
	if (!res.ok) {
		const raw = await res.text();
		const looksLikeHtml = /<!DOCTYPE|<\s*html[\s>]/i.test(raw);
		const msg = looksLikeHtml
			? `Media request failed (${res.status})`
			: raw.slice(0, 800) || `HTTP ${res.status}`;
		throw new Error(msg);
	}
	return res.json();
}

export type MediaAiContextResponse = {
	success: boolean;
	rating_key: string;
	cached?: boolean;
	plex: { title: string; year: number | null; type: string };
	wikipedia: {
		source?: string;
		url?: string;
		summary?: string;
		description?: string;
		thumbnail?: string;
	} | null;
	tmdb: {
		id: number;
		title: string;
		overview: string | null;
		poster_url: string | null;
		url: string;
		vote_average: number | null;
		release_date?: string | null;
	} | null;
	links: Record<string, string>;
	llm_notes: string | null;
};

/** Wikipedia + TMDB (with API key) + links + optional LLM notes. Uses server cache unless refresh=true. */
export async function getMediaAiContext(
	ratingKey: string,
	refresh = false,
): Promise<MediaAiContextResponse> {
	const sp = new URLSearchParams();
	if (refresh) sp.set("refresh", "1");
	const qs = sp.toString();
	const res = await fetch(
		`${getBaseUrl()}/api/media/${encodeURIComponent(ratingKey)}/ai-context${qs ? `?${qs}` : ""}`,
	);
	if (!res.ok) {
		const raw = await res.text();
		const looksLikeHtml = /<!DOCTYPE|<\s*html[\s>]/i.test(raw);
		const msg = looksLikeHtml
			? `Context request failed (${res.status})`
			: raw.slice(0, 800) || `HTTP ${res.status}`;
		throw new Error(msg);
	}
	return res.json();
}

export async function getSettings() {
	const res = await fetch(`${getBaseUrl()}/api/system/settings`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function updateSettings(body: {
	plex_token?: string;
	plex_url?: string;
	llm_provider?: string;
	llm_base_url?: string;
	llm_api_key?: string;
	tmdb_api_key?: string;
	radarr_url?: string;
	radarr_api_key?: string;
	sonarr_url?: string;
	sonarr_api_key?: string;
	lidarr_url?: string;
	lidarr_api_key?: string;
}) {
	const res = await fetch(`${getBaseUrl()}/api/system/settings`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(body),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type DialogicResult<T = unknown> = {
	success: boolean;
	message: string;
	data: T | null;
};

/** Test a Plex URL + token against the real server. Omit body to test the currently saved values. */
export async function testPlexConnection(body?: {
	plex_url?: string;
	plex_token?: string;
}): Promise<
	DialogicResult<{ friendly_name: string; version: string; machine_identifier: string | null }>
> {
	const res = await fetch(`${getBaseUrl()}/api/system/plex/test`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(body ?? {}),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Start the Plex PIN auth flow — returns a code and an app.plex.tv link to open. */
export async function createPlexPin(): Promise<
	DialogicResult<{ pin_id: number; code: string; client_id: string; auth_url: string }>
> {
	const res = await fetch(`${getBaseUrl()}/api/system/plex/pin`, { method: "POST" });
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Poll a pending Plex PIN. Once the user approves it in the browser, the token is saved server-side. */
export async function pollPlexPin(
	pinId: number,
	clientId: string,
): Promise<DialogicResult<{ authorized: boolean; token_set?: boolean }>> {
	const sp = new URLSearchParams({ client_id: clientId });
	const res = await fetch(`${getBaseUrl()}/api/system/plex/pin/${pinId}?${sp}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type DiagnosticStatus = "ok" | "warn" | "error" | "info";

export type DiagnosticCheck = {
	id: string;
	label: string;
	status: DiagnosticStatus;
	message: string;
};

export type DiagnosticsResponse = {
	success: boolean;
	overall: DiagnosticStatus;
	checks: DiagnosticCheck[];
};

/** Run every connectivity/config check at once (Plex, LLM, RAG, *arr). */
export async function getDiagnostics(): Promise<DiagnosticsResponse> {
	const res = await fetch(`${getBaseUrl()}/api/system/diagnostics`, { cache: "no-store" });
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function getLlmModels(params?: {
	provider?: string;
	base_url?: string;
}) {
	const sp = new URLSearchParams();
	if (params?.provider) sp.set("provider", params.provider);
	if (params?.base_url) sp.set("base_url", params.base_url);
	const qs = sp.toString();
	const res = await fetch(`${getBaseUrl()}/api/llm/models${qs ? `?${qs}` : ""}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type LlmProviderInfo = {
	id: string;
	label: string;
	kind: "local" | "cloud";
	base_url: string;
	needs_key: boolean;
	key_env: string | null;
	configured: boolean;
};

/** Local + cloud provider registry: which are configured, never key bytes. */
export async function getLlmProviders(): Promise<{ providers: LlmProviderInfo[] }> {
	const res = await fetch(`${getBaseUrl()}/api/llm/providers`, { cache: "no-store" });
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Save a cloud provider's API key to the backend keystore (write-only). */
export async function saveLlmProviderKey(
	provider: string,
	apiKey: string,
): Promise<{ success: boolean; error?: string }> {
	const res = await fetch(`${getBaseUrl()}/api/llm/keys/${encodeURIComponent(provider)}`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ api_key: apiKey }),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type GpuInfo = {
	index: number;
	name: string;
	total_mb: number;
	used_mb: number;
	free_mb: number;
};

/** Live GPU VRAM telemetry ([] on a GPU-less machine - not an error). */
export async function getLlmGpus(): Promise<{ gpus: GpuInfo[] }> {
	const res = await fetch(`${getBaseUrl()}/api/llm/gpus`, { cache: "no-store" });
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type LoadedModel = { name: string; size_vram_mb: number; expires_at: string };

/** Models currently resident on the local Ollama engine. */
export async function getLlmLoaded(): Promise<{ engine: boolean; models: LoadedModel[] }> {
	const res = await fetch(`${getBaseUrl()}/api/llm/loaded`, { cache: "no-store" });
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Evict Ollama models from VRAM. Omit `keep` to evict everything - the
 * escape hatch when VRAM is full and an AI task needs room to run. */
export async function unloadLlm(
	keep?: string,
): Promise<{ success: boolean; evicted: string[]; engine: boolean }> {
	const res = await fetch(`${getBaseUrl()}/api/llm/unload`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ keep: keep ?? "" }),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type SemanticResult = {
	content?: string;
	text?: string;
	metadata?: {
		title?: string;
		type?: string;
		library?: string;
		year?: number;
		start_time?: number;
		end_time?: number;
		language?: string;
		media_id?: string;
	};
	score?: number;
};

export async function getSemanticSearch(params: {
	query: string;
	limit?: number;
	index?: "metadata" | "subtitles";
}): Promise<{
	available: boolean;
	results: SemanticResult[];
	error: string | null;
}> {
	const sp = new URLSearchParams({ query: params.query });
	if (params.limit != null) sp.set("limit", String(params.limit));
	if (params.index) sp.set("index", params.index);
	const res = await fetch(`${getBaseUrl()}/api/rag/semantic?${sp}`);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Progress snapshot from GET /api/rag/sync/status (poll while reindex runs). */
export type RagSyncProgress = {
	phase: string;
	message?: string;
	libraries_total?: number;
	library_index?: number;
	library_name?: string;
	library_type?: string;
	documents_so_far?: number;
	documents_total?: number;
	indexed_count?: number;
};

export async function getRagSyncStatus(): Promise<RagSyncProgress> {
	const res = await fetch(`${getBaseUrl()}/api/rag/sync/status`, {
		cache: "no-store",
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Starts background reindex; poll {@link getRagSyncStatus} until phase is complete or error. */
export async function startRagSync(type: "metadata" | "subtitles" = "metadata"): Promise<{
	success: boolean;
	started?: boolean;
	already_running?: boolean;
	error?: string | null;
}> {
	const endpoint = type === "metadata" ? "/api/rag/sync" : "/api/rag/sync/subtitles";
	const res = await fetch(`${getBaseUrl()}${endpoint}`, { method: "POST" });
	const data = (await res.json().catch(() => ({}))) as {
		already_running?: boolean;
		error?: string;
		success?: boolean;
	};
	if (res.status === 409 && data.already_running) {
		return {
			success: false,
			already_running: true,
			error: data.error ?? "Already running",
		};
	}
	if (!res.ok) {
		throw new Error(
			typeof data.error === "string" ? data.error : (await res.text()) || `HTTP ${res.status}`,
		);
	}
	return data as { success: boolean; started?: boolean; error?: string | null };
}

const SYNC_WAIT_MAX_MS = 30 * 60 * 1000;

/** Wait until background reindex finishes (polls {@link getRagSyncStatus}). Use from pages that do not show a progress UI. */
export async function syncRag(): Promise<{
	success: boolean;
	available: boolean;
	indexed_count: number;
	message?: string;
	error: string | null;
}> {
	const start = await startRagSync();
	if (!start.success && !start.already_running) {
		return {
			success: false,
			available: false,
			indexed_count: 0,
			error: start.error ?? "Could not start reindex",
		};
	}

	const deadline = Date.now() + SYNC_WAIT_MAX_MS;
	while (Date.now() < deadline) {
		const p = await getRagSyncStatus();
		if (p.phase === "complete") {
			return {
				success: true,
				available: true,
				indexed_count: p.indexed_count ?? 0,
				message: p.message,
				error: null,
			};
		}
		if (p.phase === "error") {
			return {
				success: false,
				available: true,
				indexed_count: 0,
				error: p.message ?? "Reindex failed",
			};
		}
		await new Promise((r) => setTimeout(r, 400));
	}
	return {
		success: false,
		available: true,
		indexed_count: 0,
		error: "Reindex timed out while waiting for completion.",
	};
}

// --- Deep media enrichment ---------------------------------------------------

export type EnrichmentContentWarnings = {
	violence?: string;
	sexual_content?: string;
	language?: string;
	other_triggers?: string[];
};

export type EnrichmentReportSections = {
	synopsis?: string;
	critical_overview?: string;
	why_this_matters?: string;
	production_notes?: string;
	reception_at_release?: string;
	legacy?: string;
	content_warnings?: EnrichmentContentWarnings;
	thematic_tags?: string[];
	director_context?: string;
	key_cast_notes?: string;
	awards?: string[];
	trivia?: string[];
};

export type EnrichmentReport = {
	id: number;
	plex_rating_key: string;
	media_type: string;
	title: string;
	year: number | null;
	enrichment_version: number;
	report_sections: EnrichmentReportSections;
	sources_fetched: string[];
	sources_failed: string[];
	raw_data: Record<string, unknown>;
	themes: string[];
	director: string | null;
	tmdb_collection_id: number | null;
	fetched_at?: string;
	updated_at?: string;
	from_cache?: boolean;
};

export type EnrichOptions = {
	force_refresh?: boolean;
	sources?: string[];
	llm_provider?: string;
	llm_model?: string;
};

/** Fetch/synthesise the deep dossier for one library item (cached 90 days). */
export async function enrichMedia(
	ratingKey: string,
	opts: EnrichOptions = {},
): Promise<{ success: boolean } & EnrichmentReport> {
	const res = await fetch(`${getBaseUrl()}/api/enrichment/${encodeURIComponent(ratingKey)}`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(opts),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

/** Read a cached dossier without triggering a new fetch/synthesis. */
export async function getEnrichment(
	ratingKey: string,
): Promise<{ success: boolean; data: EnrichmentReport | null; message?: string }> {
	const res = await fetch(`${getBaseUrl()}/api/enrichment/${encodeURIComponent(ratingKey)}`, {
		cache: "no-store",
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type RelatedMediaItem = {
	source_rating_key: string;
	target_rating_key: string;
	relation_type: string;
	relation_detail: string | null;
	confidence: number;
	target_title?: string;
	target_year?: number | null;
};

/** Library items related to this one (by director, shared cast, collection, or theme). */
export async function getRelatedMedia(
	ratingKey: string,
	relationType?: string,
): Promise<{ success: boolean; data: RelatedMediaItem[]; count: number }> {
	const sp = new URLSearchParams();
	if (relationType) sp.set("relation_type", relationType);
	const qs = sp.toString();
	const res = await fetch(
		`${getBaseUrl()}/api/enrichment/${encodeURIComponent(ratingKey)}/related${qs ? `?${qs}` : ""}`,
		{ cache: "no-store" },
	);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type BulkEnrichOptions = EnrichOptions & {
	library_id?: string;
	rating_keys?: string[];
	max_items?: number;
};

/** Queue a background enrichment run over an entire library (or an explicit list of items). */
export async function startBulkEnrichment(
	opts: BulkEnrichOptions,
): Promise<{ success: boolean; job_id: string; total: number }> {
	const res = await fetch(`${getBaseUrl()}/api/enrichment/bulk`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(opts),
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type BulkEnrichmentStatus = {
	job_id: string;
	phase: "running" | "complete" | "error";
	total: number;
	done: number;
	failed: number;
	current_title: string;
	errors: { title: string; error: string }[];
	message?: string;
};

export async function getBulkEnrichmentStatus(
	jobId: string,
): Promise<{ success: boolean } & BulkEnrichmentStatus> {
	const res = await fetch(
		`${getBaseUrl()}/api/enrichment/bulk/status/${encodeURIComponent(jobId)}`,
		{
			cache: "no-store",
		},
	);
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type EnrichmentThemeHit = { plex_rating_key: string; title: string; year: number | null };

export async function searchByTheme(
	theme: string,
	limit = 50,
): Promise<{ success: boolean; data: EnrichmentThemeHit[]; count: number }> {
	const sp = new URLSearchParams({ theme, limit: String(limit) });
	const res = await fetch(`${getBaseUrl()}/api/enrichment/by-theme?${sp.toString()}`, {
		cache: "no-store",
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export async function searchByPerson(
	name: string,
	role?: string,
	limit = 50,
): Promise<{ success: boolean; data: EnrichmentThemeHit[]; count: number }> {
	const sp = new URLSearchParams({ name, limit: String(limit) });
	if (role) sp.set("role", role);
	const res = await fetch(`${getBaseUrl()}/api/enrichment/by-person?${sp.toString()}`, {
		cache: "no-store",
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type EnrichmentStats = {
	success: boolean;
	enriched_count: number;
	active_job_id: string | null;
};

export async function getEnrichmentStats(): Promise<EnrichmentStats> {
	const res = await fetch(`${getBaseUrl()}/api/enrichment/status/stats`, { cache: "no-store" });
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

export type StaleEnrichment = {
	plex_rating_key: string;
	title: string;
	year: number | null;
	updated_at: string;
};

export async function getStaleEnrichments(
	days = 90,
): Promise<{ success: boolean; data: StaleEnrichment[]; count: number }> {
	const sp = new URLSearchParams({ days: String(days) });
	const res = await fetch(`${getBaseUrl()}/api/enrichment/status/stale?${sp.toString()}`, {
		cache: "no-store",
	});
	if (!res.ok) throw new Error(await res.text());
	return res.json();
}

// --- Taste modelling ---------------------------------------------------------

export type TasteKind = "movie" | "show";

export type TasteDimension = {
	dimension: string;
	score: number;
	watch_share: number;
	library_share: number;
	library_count: number;
	attention: number;
	strength: number;
};

export type TasteProfile = {
	success: boolean;
	built: boolean;
	error_code?: string;
	message?: string;
	kind: TasteKind;
	time_bucket: string | null;
	prefix: string | null;
	scored_dimensions: number;
	library_items: number;
	likes: TasteDimension[];
	dislikes: TasteDimension[];
};

export type TasteStatus = {
	success: boolean;
	events: number;
	dimensions: number;
	library_items: number;
	last_history_ts: string | null;
	rebuilt_at: string | null;
	built: boolean;
	running: boolean;
	progress: { phase: string; message: string; done?: number; total?: number };
};

export type TasteShift = {
	dimension: string;
	score_then: number | null;
	score_now: number;
	delta: number;
	new: boolean;
};

async function tasteFetch<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(`${getBaseUrl()}/api/taste${path}`, { cache: "no-store", ...init });
	if (!res.ok) {
		let detail = "";
		try {
			detail = (await res.json()).detail ?? "";
		} catch {
			detail = await res.text();
		}
		throw new Error(detail || `HTTP ${res.status}`);
	}
	return res.json();
}

export function getTasteStatus(): Promise<TasteStatus> {
	return tasteFetch("/status");
}

export function getTasteProfile(params: {
	kind: TasteKind;
	bucket?: string | null;
	prefix?: string | null;
	top?: number;
}): Promise<TasteProfile> {
	const sp = new URLSearchParams({ kind: params.kind, top: String(params.top ?? 25) });
	if (params.bucket) sp.set("bucket", params.bucket);
	if (params.prefix) sp.set("prefix", params.prefix);
	return tasteFetch(`/profile?${sp.toString()}`);
}

export function getTasteShifts(params: {
	kind: TasteKind;
	days: number;
	prefix?: string | null;
	top?: number;
}): Promise<{ success: boolean; built: boolean; shifts: TasteShift[] }> {
	const sp = new URLSearchParams({
		kind: params.kind,
		days: String(params.days),
		top: String(params.top ?? 10),
	});
	if (params.prefix) sp.set("prefix", params.prefix);
	return tasteFetch(`/recent-shifts?${sp.toString()}`);
}

/** Rebuild the whole profile from Plex history. Runs in the background: poll getTasteStatus. */
export function startTasteRebuild(
	opts: { refresh_baseline?: boolean } = {},
): Promise<{ success: boolean }> {
	return tasteFetch("/rebuild", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(opts),
	});
}

export function syncTaste(): Promise<{ success: boolean; events_new?: number; message?: string }> {
	return tasteFetch("/sync", { method: "POST" });
}
