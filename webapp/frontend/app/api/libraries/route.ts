import { NextRequest } from "next/server";
import { proxyGet } from "@/lib/proxy";

export async function GET(request: NextRequest) {
  try {
    return await proxyGet("/api/libraries/");
  } catch {
    return new Response(null, { status: 502 });
  }
}
