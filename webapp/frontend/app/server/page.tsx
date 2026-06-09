"use client";

import { ServerInfoView } from "@/components/server/server-info-view";
import { ErrorBanner } from "@/components/ui/error-banner";
import { getServerInfo } from "@/utils/api";
import { PLEX_TOKEN_HINT } from "@/utils/config-hints";
import { useEffect, useState } from "react";

export default function ServerPage() {
	const [data, setData] = useState<Record<string, unknown> | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		let cancelled = false;
		getServerInfo()
			.then((res) => {
				if (!cancelled) setData(res as Record<string, unknown>);
			})
			.catch(() => {
				if (!cancelled) setData(null);
			})
			.finally(() => {
				if (!cancelled) setLoading(false);
			});
		return () => {
			cancelled = true;
		};
	}, []);

	return (
		<div className="container mx-auto p-6 max-w-5xl">
			<h1 className="text-3xl font-bold mb-2 text-slate-100">Server</h1>
			<p className="text-slate-500 text-sm mb-6">
				Plex Media Server summary from the MCP{" "}
				<code className="text-amber text-xs">plex_server</code> tool (
				<code className="text-amber text-xs">info</code>). Use{" "}
				<strong className="text-slate-400">Overview</strong> for readable fields or{" "}
				<strong className="text-slate-400">Raw JSON</strong> for the full response.
			</p>
			{loading ? (
				<p className="text-slate-400">Loading server info…</p>
			) : data === null ? (
				<ErrorBanner
					title="Could not load server info"
					message="Backend unavailable or Plex not configured."
					hint={PLEX_TOKEN_HINT}
					actionHref="/settings"
					actionLabel="Open Settings → Plex"
				/>
			) : (
				<ServerInfoView payload={data} />
			)}
		</div>
	);
}
