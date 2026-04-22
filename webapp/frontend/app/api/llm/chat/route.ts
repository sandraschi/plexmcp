import type { NextRequest } from "next/server";

const BACKEND_URL = (
	process.env.API_URL ||
	process.env.NEXT_PUBLIC_API_URL ||
	"http://127.0.0.1:10740"
).replace("localhost", "127.0.0.1");

export async function POST(request: NextRequest) {
	try {
		const body = await request.json();
		const res = await fetch(`${BACKEND_URL}/api/llm/chat`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body),
		});
		const text = await res.text();
		if (!res.ok) {
			return new Response(text, { status: res.status });
		}
		return new Response(text, {
			status: 200,
			headers: { "Content-Type": res.headers.get("content-type") ?? "application/json" },
		});
	} catch {
		return new Response(null, { status: 502 });
	}
}
