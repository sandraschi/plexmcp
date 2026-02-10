import { NextRequest } from "next/server";
import { proxyGet } from "@/lib/proxy";

const BACKEND_URL = (
  process.env.API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:10740"
).replace("localhost", "127.0.0.1");

export async function GET(request: NextRequest) {
  try {
    return await proxyGet("/api/system/settings");
  } catch {
    return new Response(null, { status: 502 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const body = await request.json();
    const res = await fetch(`${BACKEND_URL}/api/system/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) return new Response(JSON.stringify(data), { status: res.status });
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return new Response(null, { status: 502 });
  }
}
