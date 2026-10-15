"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import { getCapabilities } from "@/utils/api";
import { BACKEND_DOWN_HINT } from "@/utils/config-hints";
import { Terminal } from "lucide-react";
import { useEffect, useState } from "react";

type Capabilities = {
	name: string;
	version: string;
	transports: string[];
	tool_count: number;
	tool_categories: string[];
	features: Record<string, boolean>;
	endpoints_canonical: string[];
	endpoints_legacy_alias: string[];
};

export default function ToolsPage() {
	const [caps, setCaps] = useState<Capabilities | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const load = async () => {
		setLoading(true);
		setError(null);
		try {
			setCaps(await getCapabilities());
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e));
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		load();
	}, []);

	return (
		<div className="container mx-auto p-6 max-w-6xl" data-testid="tools-page">
			<div className="flex items-start gap-3 mb-2">
				<Terminal className="w-7 h-7 text-amber shrink-0 mt-0.5" />
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Tools</h1>
					<p className="text-slate-500 mt-1 text-sm">
						Raw view over the MCP tool surface — what agents see.{" "}
						{caps && (
							<span data-testid="tools-count">
								{caps.tool_count} tools · {caps.tool_categories.length} categories · {caps.name} v
								{caps.version} ({caps.transports.join(", ")})
							</span>
						)}
					</p>
				</div>
				<button
					type="button"
					data-testid="tools-refresh"
					onClick={load}
					className="ml-auto px-4 py-2 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors shrink-0"
				>
					Refresh
				</button>
			</div>

			{loading ? (
				<p className="text-slate-500 mt-6" data-testid="tools-loading">
					Loading tool surface…
				</p>
			) : error ? (
				<div className="mt-6" data-testid="tools-error">
					<ErrorBanner title="Tools unavailable" message={error} hint={BACKEND_DOWN_HINT} />
					<button
						type="button"
						onClick={load}
						className="mt-3 px-4 py-2 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
					>
						Retry
					</button>
				</div>
			) : !caps ? (
				<p className="text-sm text-slate-500 mt-6" data-testid="tools-empty">
					No tool data returned.
				</p>
			) : (
				<div className="mt-6 space-y-6">
					<section aria-label="Tool categories">
						<h2 className="text-sm uppercase tracking-wide text-slate-500 mb-3">
							Categories · {caps.tool_categories.length}
						</h2>
						<ul className="flex flex-wrap gap-2">
							{caps.tool_categories.map((c) => (
								<li
									key={c}
									data-testid={`tools-category-${c}`}
									className="px-3 py-1.5 rounded-lg glass-panel border border-slate-600/50 text-sm text-slate-300 font-mono text-xs"
								>
									{c}
								</li>
							))}
						</ul>
						<p className="text-xs text-slate-600 mt-2">
							Portmanteau tools: plex_library, plex_media, plex_search, plex_streaming, plex_server,
							plex_user, plex_playlist, plex_collections, plex_metadata, plex_organization,
							plex_performance, plex_quality, plex_reporting, plex_rag, plex_help, plex_shutdown,
							plex_integration, plex_media_enrichment, plex_audio_mgr, plex_ffmpeg_mgr, arr_stack,
							plex_taste — plus sampling tools agentic_plex_workflow and plex_natural_assistant.
						</p>
					</section>
					<section aria-label="Canonical endpoints">
						<h2 className="text-sm uppercase tracking-wide text-slate-500 mb-3">
							Canonical REST endpoints · {caps.endpoints_canonical.length}
						</h2>
						<ul className="rounded-xl glass-panel border border-slate-600/50 divide-y divide-slate-700/50">
							{caps.endpoints_canonical.map((e) => (
								<li key={e} className="px-4 py-2 font-mono text-xs text-slate-300">
									{e}
								</li>
							))}
						</ul>
					</section>
					<section aria-label="Legacy aliases">
						<h2 className="text-sm uppercase tracking-wide text-slate-500 mb-3">
							Legacy aliases (kept working)
						</h2>
						<ul className="rounded-xl glass-panel border border-slate-600/50 divide-y divide-slate-700/50">
							{caps.endpoints_legacy_alias.map((e) => (
								<li key={e} className="px-4 py-2 font-mono text-xs text-slate-500">
									{e}
								</li>
							))}
						</ul>
					</section>
				</div>
			)}
		</div>
	);
}
