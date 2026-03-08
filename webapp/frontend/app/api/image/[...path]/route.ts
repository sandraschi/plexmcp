import { NextRequest } from "next/server";
import { proxyGet } from "@/utils/proxy";

/** Proxy image requests to backend /image/... (Plex thumbnails). */
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path?.length ? path.join("/") : "";
  if (!pathStr) {
    return new Response(null, { status: 404 });
  }
  try {
    return await proxyGet(`/image/${pathStr}`);
  } catch {
    return new Response(null, { status: 502 });
  }
}
