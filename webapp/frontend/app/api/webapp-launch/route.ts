import { NextRequest } from "next/server";
import { proxyPost } from "@/utils/proxy";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    return await proxyPost("/api/webapp-launch", body, { timeoutMs: 95000 });
  } catch {
    return new Response(JSON.stringify({ error: "Backend unreachable" }), { status: 502 });
  }
}
