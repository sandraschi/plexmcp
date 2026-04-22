import { proxyGet } from "@/utils/proxy";
import type { NextRequest } from "next/server";

export async function GET(
	request: NextRequest,
	{ params }: { params: Promise<{ rating_key: string }> },
) {
	try {
		const { rating_key } = await params;
		if (!rating_key) {
			return new Response(null, { status: 400 });
		}
		const segment = encodeURIComponent(rating_key);
		const sp = request.nextUrl.searchParams;
		return await proxyGet(`/api/media/${segment}/ai-context`, sp);
	} catch {
		return new Response(null, { status: 502 });
	}
}
