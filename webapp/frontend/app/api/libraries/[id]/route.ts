import { NextRequest } from "next/server";
import { proxyGet } from "@/utils/proxy";

export async function GET(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    return await proxyGet(`/api/libraries/${id}`);
  } catch {
    return new Response(null, { status: 502 });
  }
}
