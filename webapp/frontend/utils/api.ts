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
