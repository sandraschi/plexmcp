"use client";

import { ArrStackCard } from "@/components/overview/arr-stack-card";
import { ErrorBanner } from "@/components/ui/error-banner";
import { type ArrStackResponse, getArrStackStatus, getServerStatus } from "@/utils/api";
import { Library, Search, Server } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { BACKEND_DOWN_HINT, PLEX_TOKEN_HINT } from "@/utils/config-hints";

export default function Home() {
	const [status, setStatus] = useState<{
		success?: boolean;
		message?: string;
		[key: string]: unknown;
	} | null>(null);
	const [arrStatus, setArrStatus] = useState<ArrStackResponse | null>(null);
	const [loading, setLoading] = useState(true);

	const retryCount = useRef(0);

	useEffect(() => {
		let cancelled = false;
		const fetchWithRetry = async () => {
			while (!cancelled) {
				try {
					const s = await getServerStatus();
					if (!cancelled) {
						setStatus(s);
						retryCount.current = 0;
						break;
					}
				} catch {
					if (cancelled) return;
					const delay = Math.min(1000 * Math.pow(2, retryCount.current), 30000);
					retryCount.current++;
					setStatus(null);
					await new Promise((r) => setTimeout(r, delay));
				}
			}
		};
		(async () => {
			await fetchWithRetry();
			try {
				const a = await getArrStackStatus();
				if (!cancelled) setArrStatus(a);
			} catch {
				if (!cancelled) setArrStatus(null);
			}
			if (!cancelled) setLoading(false);
		})();
		return () => {
			cancelled = true;
		};
	}, []);

	const cards = [
		{ href: "/libraries", label: "Libraries", icon: Library },
		{ href: "/search", label: "Search", icon: Search },
		{ href: "/server", label: "Server", icon: Server },
	];

	return (
		<main className="min-h-screen">
			<div className="container mx-auto p-6">
				<h1 className="text-3xl font-bold mb-2 text-slate-100">Overview</h1>
				{loading ? (
					<p className="text-slate-400 mb-6">Connecting…</p>
				) : status === null ? (
					<ErrorBanner
						title="Backend unavailable"
						message="Could not connect to the Plex MCP backend on port 10740."
						hint={BACKEND_DOWN_HINT}
					/>
				) : status.success ? (
					<p className="text-slate-500 mb-6">{String(status.message ?? "Connected to Plex")}</p>
				) : (
					<ErrorBanner
						title="Plex not connected"
						message={String(status.message ?? status.error ?? "Could not reach Plex server.")}
						hint={PLEX_TOKEN_HINT}
						actionHref="/settings"
						actionLabel="Open Settings → Plex"
					/>
				)}
				<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{cards.map(({ href, label, icon: Icon }) => (
						<Link
							key={href}
							href={href}
							className="flex items-center gap-3 p-6 rounded-xl glass-panel border-slate-600/50 hover:border-amber/40 transition-colors"
						>
							<Icon className="w-8 h-8 text-amber shrink-0" />
							<span className="text-slate-200 font-medium">{label}</span>
						</Link>
					))}
				</div>

				<div className="mt-8 max-w-lg">
					<ArrStackCard data={arrStatus} />
				</div>
			</div>
		</main>
	);
}
