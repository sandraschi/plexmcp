import { proxyPost } from "@/utils/proxy";

const SYNC_TIMEOUT_MS = 300000; // 5 min for large libraries

export async function POST() {
  try {
    return await proxyPost("/api/rag/sync", {}, { timeoutMs: SYNC_TIMEOUT_MS });
  } catch {
    return new Response(null, { status: 502 });
  }
}
