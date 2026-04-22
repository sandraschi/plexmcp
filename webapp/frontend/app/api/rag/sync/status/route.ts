import { proxyGet } from "@/utils/proxy";

export async function GET() {
	return proxyGet("/api/rag/sync/status");
}
