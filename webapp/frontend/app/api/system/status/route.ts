import { NextRequest } from "next/server";
import { proxyGet } from "@/utils/proxy";

export async function GET(request: NextRequest) {
  try {
    return await proxyGet("/api/system/status");
  } catch {
    return new Response(null, { status: 502 });
  }
}
