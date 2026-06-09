import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:10740";
const PROXY_TIMEOUT_MS = 15000;
const debugProxy = process.env.NEXT_DEBUG_PROXY === "1";

export async function proxyGet(
	path: string,
	searchParams?: URLSearchParams | string,
): Promise<NextResponse> {
	const url = searchParams
		? `${BACKEND_URL}${path}?${typeof searchParams === "string" ? searchParams : searchParams.toString()}`
		: `${BACKEND_URL}${path}`;

	if (debugProxy) {
		console.error(`[PROXY] GET ${url}`);
	}

	const controller = new AbortController();
	const t = setTimeout(() => controller.abort(), PROXY_TIMEOUT_MS);
	try {
		const res = await fetch(url, {
			signal: controller.signal,
			cache: "no-store",
		});
		if (debugProxy) {
			console.error(`[PROXY] Response status: ${res.status}`);
		}

		if (!res.ok) {
			let errBody: { error?: string; detail?: string } = {
				error: `Backend returned ${res.status}`,
			};
			try {
				const text = await res.text();
				if (text) {
					try {
						errBody = JSON.parse(text);
					} catch {
						errBody = { error: text.slice(0, 500) };
					}
				}
			} catch {
				/* ignore */
			}
			return NextResponse.json(errBody, { status: res.status });
		}
		return new NextResponse(res.body, {
			status: res.status,
			headers: {
				"Content-Type": res.headers.get("content-type") ?? "application/json",
			},
		});
	} catch (err) {
		console.error("[PROXY] Error:", err);
		throw err;
	} finally {
		clearTimeout(t);
	}
}

export async function proxyPost(
	path: string,
	body: unknown,
	options?: { timeoutMs?: number },
): Promise<NextResponse> {
	const timeout = options?.timeoutMs ?? PROXY_TIMEOUT_MS;
	const url = `${BACKEND_URL}${path}`;
	const controller = new AbortController();
	const t = setTimeout(() => controller.abort(), timeout);
	try {
		const res = await fetch(url, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(body),
			signal: controller.signal,
			cache: "no-store",
		});
		clearTimeout(t);
		if (!res.ok) {
			let errBody: { error?: string; detail?: string } = {
				error: `Backend returned ${res.status}`,
			};
			try {
				const text = await res.text();
				if (text) {
					try {
						errBody = JSON.parse(text);
					} catch {
						errBody = { error: text.slice(0, 500) };
					}
				}
			} catch {
				/* ignore */
			}
			return NextResponse.json(errBody, { status: res.status });
		}
		const text = await res.text();
		if (!text) return NextResponse.json({ error: "Empty response" }, { status: 502 });
		const data = JSON.parse(text);
		return NextResponse.json(data);
	} catch (e) {
		clearTimeout(t);
		throw e;
	}
}
