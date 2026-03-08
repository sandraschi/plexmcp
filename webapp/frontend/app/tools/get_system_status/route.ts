import { NextRequest } from "next/server";
import { proxyGet, proxyPost } from "@/utils/proxy";

/** Handle OPTIONS so MCP clients probing /tools/get_system_status get 204 instead of 404. */
export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      Allow: "GET, POST, OPTIONS",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

/** Proxy to backend server status; some MCP clients expect system status at this path. */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    return await proxyGet("/api/server/status", searchParams);
  } catch {
    return new Response(null, { status: 502 });
  }
}

/** POST: same as GET (some MCP clients call this path with POST). */
export async function POST() {
  try {
    return await proxyGet("/api/server/status");
  } catch {
    return new Response(null, { status: 502 });
  }
}
