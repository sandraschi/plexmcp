"use client";

import { useState, useEffect } from "react";
import { getSettings, updateSettings, getLlmModels } from "@/lib/api";

const DEFAULT_MOVIES_LIBRARY_KEY = "plex-webapp-default-movies-library";
const DEFAULT_LLM_MODEL_KEY = "plex-webapp-default-llm-model";

interface SettingsClientProps {
  settings: {
    plex_token_set?: boolean;
    plex_token?: string | null;
    plex_url?: string | null;
    llm_provider?: string | null;
    llm_base_url?: string | null;
    llm_api_key_set?: boolean;
    llm_api_key?: string | null;
    api_version?: string;
  };
}

export function SettingsClient({ settings }: SettingsClientProps) {
  const [plexToken, setPlexToken] = useState("");
  const [plexUrl, setPlexUrl] = useState("");
  const [llmProvider, setLlmProvider] = useState("ollama");
  const [llmBaseUrl, setLlmBaseUrl] = useState("");
  const [llmApiKey, setLlmApiKey] = useState("");
  const [defaultLlmModel, setDefaultLlmModel] = useState("");
  const [defaultMoviesLibrary, setDefaultMoviesLibrary] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "ok" | "err"; text: string } | null>(null);

  useEffect(() => {
    setPlexUrl(settings.plex_url ?? "");
    setLlmProvider(settings.llm_provider ?? "ollama");
    setLlmBaseUrl(settings.llm_base_url ?? "");
    if (typeof window !== "undefined") {
      setDefaultMoviesLibrary(localStorage.getItem(DEFAULT_MOVIES_LIBRARY_KEY) ?? "");
      setDefaultLlmModel(localStorage.getItem(DEFAULT_LLM_MODEL_KEY) ?? "");
    }
    getLlmModels()
      .then((d: { models?: string[] }) => setModels(d.models ?? []))
      .catch(() => setModels([]));
  }, [settings]);

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const body: Record<string, string> = {};
      if (plexToken.trim()) body.plex_token = plexToken.trim();
      if (plexUrl.trim()) body.plex_url = plexUrl.trim();
      if (llmProvider) body.llm_provider = llmProvider;
      if (llmBaseUrl.trim()) body.llm_base_url = llmBaseUrl.trim();
      if (llmApiKey.trim()) body.llm_api_key = llmApiKey.trim();
      await updateSettings(body);
      if (typeof window !== "undefined") {
        if (defaultMoviesLibrary) localStorage.setItem(DEFAULT_MOVIES_LIBRARY_KEY, defaultMoviesLibrary);
        else localStorage.removeItem(DEFAULT_MOVIES_LIBRARY_KEY);
        if (defaultLlmModel) localStorage.setItem(DEFAULT_LLM_MODEL_KEY, defaultLlmModel);
        else localStorage.removeItem(DEFAULT_LLM_MODEL_KEY);
      }
      setMessage({ type: "ok", text: "Settings saved." });
      if (plexToken.trim()) setPlexToken("");
      if (llmApiKey.trim()) setLlmApiKey("");
    } catch (e) {
      setMessage({ type: "err", text: e instanceof Error ? e.message : "Save failed" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-8">
      <section className="rounded-xl glass-panel border border-slate-600/50 p-6">
        <h2 className="text-lg font-semibold text-amber mb-4">Plex</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">API key (X-Plex-Token)</label>
            <input
              type="password"
              value={plexToken}
              onChange={(e) => setPlexToken(e.target.value)}
              placeholder={settings.plex_token_set ? "Leave blank to keep current" : "Your Plex token"}
              className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Plex URL</label>
            <input
              type="url"
              value={plexUrl}
              onChange={(e) => setPlexUrl(e.target.value)}
              placeholder="http://localhost:32400"
              className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
            />
          </div>
        </div>
      </section>

      <section className="rounded-xl glass-panel border border-slate-600/50 p-6">
        <h2 className="text-lg font-semibold text-amber mb-4">LLM</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Provider</label>
            <select
              value={llmProvider}
              onChange={(e) => setLlmProvider(e.target.value)}
              className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm"
            >
              <option value="ollama">Ollama</option>
              <option value="lmstudio">LM Studio</option>
              <option value="openai">OpenAI-compatible</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Base URL</label>
            <input
              type="url"
              value={llmBaseUrl}
              onChange={(e) => setLlmBaseUrl(e.target.value)}
              placeholder="http://127.0.0.1:11434"
              className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">API key (optional)</label>
            <input
              type="password"
              value={llmApiKey}
              onChange={(e) => setLlmApiKey(e.target.value)}
              placeholder={settings.llm_api_key_set ? "Leave blank to keep current" : "For OpenAI-compatible"}
              className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-400 mb-1">Default model (for Chat, saved in browser)</label>
            <select
              value={defaultLlmModel}
              onChange={(e) => setDefaultLlmModel(e.target.value)}
              className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 text-sm"
            >
              <option value="">Select after loading...</option>
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <p className="text-xs text-slate-500 mt-1">Fetched from LLM endpoint. Save to store preference.</p>
          </div>
        </div>
      </section>

      <section className="rounded-xl glass-panel border border-slate-600/50 p-6">
        <h2 className="text-lg font-semibold text-amber mb-4">Client preferences</h2>
        <div className="space-y-2">
          <label className="block text-sm text-slate-400">Default movies library (saved in browser)</label>
          <input
            type="text"
            value={defaultMoviesLibrary}
            onChange={(e) => setDefaultMoviesLibrary(e.target.value)}
            placeholder="Library key or leave empty"
            className="w-full px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-slate-200 placeholder-slate-500 text-sm"
          />
        </div>
      </section>

      {message && (
        <p className={message.type === "ok" ? "text-green-400 text-sm" : "text-amber text-sm"}>
          {message.text}
        </p>
      )}
      <button
        type="button"
        onClick={handleSave}
        disabled={saving}
        className="px-6 py-3 rounded-xl bg-amber text-slate-900 font-medium hover:bg-amber/90 disabled:opacity-50"
      >
        {saving ? "Saving..." : "Save settings"}
      </button>
    </div>
  );
}
