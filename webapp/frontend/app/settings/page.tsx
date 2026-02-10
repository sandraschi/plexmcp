import { getSettings } from "@/lib/api";
import { ErrorBanner } from "@/components/ui/error-banner";
import { SettingsClient } from "./settings-client";

export default async function SettingsPage() {
  let settings: {
    plex_token_set?: boolean;
    plex_token?: string | null;
    plex_url?: string | null;
    llm_provider?: string | null;
    llm_base_url?: string | null;
    llm_api_key_set?: boolean;
    llm_api_key?: string | null;
    api_version?: string;
  } | null = null;

  try {
    settings = await getSettings();
  } catch {
    settings = null;
  }

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <h1 className="text-3xl font-bold mb-2 text-slate-100">Settings</h1>
      <p className="text-slate-500 mb-6">
        Connection status and client preferences. Backend config is in
        webapp/backend/.env
      </p>
      {settings === null ? (
        <ErrorBanner
          title="Could not load settings"
          message="Backend unavailable."
          hint="Ensure the backend is running on port 10740"
        />
      ) : (
        <SettingsClient settings={settings} />
      )}
    </div>
  );
}
