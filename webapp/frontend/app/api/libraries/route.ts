import { NextRequest } from "next/server";
import { proxyGet } from "@/utils/proxy";

export async function GET(request: NextRequest) {
  try {
    console.error(`[ROUTE] GET /api/libraries/ - calling proxy`);
    const result = await proxyGet("/api/libraries/");
    console.error(`[ROUTE] GET /api/libraries/ - proxy returned status ${result.status} `);
    return result;
  } catch (err) {
    console.error(`[ROUTE] GET /api/libraries/ - error: `, err);
    return new Response(null, { status: 502 });
  }
}
