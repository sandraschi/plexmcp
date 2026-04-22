import { proxyGet } from "@/utils/proxy";

export async function GET() {
	return proxyGet("/api/arr/status");
}
