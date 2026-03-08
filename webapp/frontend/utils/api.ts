export function getBaseUrl(): string {
  if (typeof window !== "undefined") return "";
  return process.env.NEXT_PUBLIC_APP_URL ?? "http://127.0.0.1:10741";
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

export async function listLibraries() {
  const res = await fetch(`${getBaseUrl()}/api/libraries/`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function search(params?: { query?: string; library_id?: string; limit?: number }) {
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
}) {
  const res = await fetch(`${getBaseUrl()}/api/system/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getLlmModels() {
  const res = await fetch(`${getBaseUrl()}/api/llm/models`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export interface SemanticResult {
  content?: string;
  text?: string;
  metadata?: { title?: string; type?: string; library?: string; year?: number };
  score?: number;
}

export async function getSemanticSearch(params: {
  query: string;
  limit?: number;
}): Promise<{ available: boolean; results: SemanticResult[]; error: string | null }> {
  const sp = new URLSearchParams({ query: params.query });
  if (params.limit != null) sp.set("limit", String(params.limit));
  const res = await fetch(`${getBaseUrl()}/api/rag/semantic?${sp}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function syncRag(): Promise<{
  success: boolean;
  available: boolean;
  indexed_count: number;
  message?: string;
  error: string | null;
}> {
  const res = await fetch(`${getBaseUrl()}/api/rag/sync`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
