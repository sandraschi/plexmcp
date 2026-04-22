import { proxyGet } from "@/utils/proxy";
import type { NextRequest } from "next/server";

export async function GET(_request: NextRequest) {
	try {
		return await proxyGet("/health");
	} catch {
		return new Response(null, { status: 502 });
	}
}
