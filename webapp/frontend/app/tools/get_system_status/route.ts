import { NextRequest } from "next/server";
import { proxyGet } from "@/utils/proxy";

/** Handle OPTIONS so MCP clients probing /tools/get_system_status get 200 instead of 404. */
export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      Allow: "GET, OPTIONS",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
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
