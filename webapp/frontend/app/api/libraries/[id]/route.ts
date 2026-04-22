import { proxyGet } from "@/utils/proxy";
import type { NextRequest } from "next/server";

export async function GET(_request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
	try {
		const { id } = await params;
		return await proxyGet(`/api/libraries/${id}`);
	} catch {
		return new Response(null, { status: 502 });
	}
}
