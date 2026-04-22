import { proxyGet } from "@/utils/proxy";
import type { NextRequest } from "next/server";

export async function GET(
	_request: NextRequest,
	{ params }: { params: Promise<{ rating_key: string }> },
) {
	try {
		const { rating_key } = await params;
		if (!rating_key) {
			return new Response(null, { status: 400 });
		}
		const segment = encodeURIComponent(rating_key);
		return await proxyGet(`/api/media/${segment}`);
	} catch {
		return new Response(null, { status: 502 });
	}
}
