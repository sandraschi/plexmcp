import { getServerInfo } from "@/utils/api";
import { ErrorBanner } from "@/components/ui/error-banner";

export default async function ServerPage() {
  let data: Record<string, unknown> | null = null;
  try {
    data = await getServerInfo();
  } catch {
    data = null;
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-slate-100">Server</h1>
      {data === null ? (
        <ErrorBanner
          title="Could not load server info"
          message="Backend unavailable or PLEX_TOKEN not configured."
          hint="Set PLEX_TOKEN in webapp/backend/.env"
        />
      ) : (
        <pre className="p-4 rounded-lg bg-slate-800 text-sm text-slate-300 overflow-auto max-h-[70vh]">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
