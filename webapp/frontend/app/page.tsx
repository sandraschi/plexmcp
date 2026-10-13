"use client";

import { ArrStackCard } from "@/components/overview/arr-stack-card";
import { ErrorBanner } from "@/components/ui/error-banner";
import {
	type ArrStackResponse,
	type DashboardResponse,
	getArrStackStatus,
	getDashboard,
	getServerStatus,
} from "@/utils/api";
import { BACKEND_DOWN_HINT, PLEX_TOKEN_HINT } from "@/utils/config-hints";
import {
	Activity,
	Database,
	Film,
	Fingerprint,
	Layers,
	Library,
	MessageSquare,
	Search,
	Server,
	Settings,
	Sparkles,
} from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

function KpiCard({
	testId,
	href,
	icon: Icon,
	label,
	value,
	sub,
}: {
	testId: string;
	href: string;
	icon: typeof Library;
	label: string;
	value: string;
	sub: string;
}) {
	return (
		<Link
			href={href}
			data-testid={testId}
			className="rounded-xl glass-panel border border-slate-600/50 p-4 hover:border-amber/40 transition-colors block"
		>
			<div className="flex items-center gap-2 mb-1">
				<Icon className="w-5 h-5 text-amber shrink-0" />
				<span className="text-xs uppercase tracking-wide text-slate-500">{label}</span>
			</div>
			<div className="text-2xl font-semibold text-slate-100 truncate">{value}</div>
			<div className="text-xs text-slate-500 truncate mt-1">{sub}</div>
		</Link>
	);
}

export default function Home() {
	const [status, setStatus] = useState<{
		success?: boolean;
		message?: string;
		[key: string]: unknown;
	} | null>(null);
	const [arrStatus, setArrStatus] = useState<ArrStackResponse | null>(null);
	const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
	const [loading, setLoading] = useState(true);
	const [backendDown, setBackendDown] = useState(false);

	const retryCount = useRef(0);

	useEffect(() => {
		let cancelled = false;
		const load = async () => {
			// Prefer the aggregated endpoint; fall back to the two legacy calls.
			try {
				const d = await getDashboard();
				if (cancelled) return;
				setDashboard(d);
				setStatus(d.server);
				if (d.arr) setArrStatus(d.arr);
				setBackendDown(false);
				retryCount.current = 0;
				if (!d.arr) {
					try {
						const a = await getArrStackStatus();
						if (!cancelled) setArrStatus(a);
					} catch {
						/* arr optional */
					}
				}
			} catch {
				// Legacy path: backend may predate /api/dashboard.
				while (!cancelled) {
					try {
						const s = await getServerStatus();
						if (cancelled) return;
						setStatus(s);
						retryCount.current = 0;
						break;
					} catch {
						if (cancelled) return;
						const delay = Math.min(1000 * 2 ** retryCount.current, 30000);
						retryCount.current++;
						setStatus(null);
						setBackendDown(true);
						await new Promise((r) => setTimeout(r, delay));
						if (retryCount.current > 2) break;
					}
				}
				try {
					const a = await getArrStackStatus();
					if (!cancelled) setArrStatus(a);
				} catch {
					if (!cancelled) setArrStatus(null);
				}
			}
			if (!cancelled) setLoading(false);
		};
		load();
		return () => {
			cancelled = true;
		};
	}, []);

	const plexConnected = Boolean(status?.success);
	const showOnboardingCue = !loading && !backendDown && !plexConnected;

	const libCount = dashboard?.libraries.count;
	const libTypes = dashboard?.libraries.types ?? {};
	const libTypeSummary =
		Object.entries(libTypes).length > 0
			? Object.entries(libTypes)
					.map(([t, n]) => `${n} ${t}`)
					.join(" · ")
			: "No library data yet";
	const enrichedCount = dashboard?.enrichment.enriched_count;
	const ragAvailable = dashboard?.rag.available;
	const ragIndexed = dashboard?.rag.indexed_count;
	const ragPhase = dashboard?.rag_sync?.phase;
	const tasteBuilt = dashboard?.taste.built;
	const tasteEvents = dashboard?.taste.events;
	const llmConfigured = dashboard?.llm?.providers.filter((p) => p.configured).length;

	const actions = [
		{ href: "/libraries", label: "Browse libraries", icon: Library },
		{ href: "/search", label: "Search media", icon: Search },
		{ href: "/search/semantic", label: "Semantic search", icon: Sparkles },
		{ href: "/chat", label: "Ask chat", icon: MessageSquare },
		{ href: "/enrichment", label: "Enrich media", icon: Film },
		{ href: "/settings", label: "Settings", icon: Settings },
	];

	return (
		<main className="min-h-screen" data-testid={loading ? undefined : "dashboard-ready"}>
			<div className="container mx-auto p-6 max-w-6xl">
				{/* Hero: brand + headline + CTA (fleet gate 1) */}
				<section className="rounded-2xl glass-panel border border-slate-600/50 p-6 sm:p-8 mb-6">
					<div className="flex items-center gap-2 text-amber text-sm font-medium mb-2">
						<Film className="w-5 h-5" />
						<span>PlexMCP</span>
						<span className="text-slate-500 font-normal">· Plex Media Server console</span>
					</div>
					<h1 className="text-3xl sm:text-4xl font-bold text-slate-100 mb-2">
						Your Plex library, searchable and enriched.
					</h1>
					<p className="text-slate-400 mb-6 max-w-2xl">
						Browse libraries, run keyword and semantic search, build deep media dossiers, and track
						your taste profile - all from one dashboard.
					</p>
					<div className="flex flex-wrap gap-3">
						<Link
							href="/libraries"
							data-testid="dashboard-hero-cta"
							className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-amber text-slate-950 font-semibold hover:bg-amber/90 transition-colors"
						>
							<Library className="w-4 h-4" />
							Browse libraries
						</Link>
						<Link
							href="/search"
							className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-slate-600 text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
						>
							<Search className="w-4 h-4" />
							Search media
						</Link>
						<Link
							href="/chat"
							className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-slate-600 text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
						>
							<MessageSquare className="w-4 h-4" />
							Ask chat
						</Link>
					</div>
					{showOnboardingCue && (
						<Link
							href="/settings"
							data-testid="onboarding-cue"
							className="mt-4 flex items-center justify-center gap-2 w-full px-5 py-3 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-500 transition-colors"
						>
							<Settings className="w-4 h-4" />
							Complete onboarding - connect Plex
						</Link>
					)}
				</section>

				{loading ? (
					<p className="text-slate-400 mb-6">Connecting…</p>
				) : backendDown && status === null ? (
					<div className="mb-6">
						<ErrorBanner
							title="Backend unavailable"
							message="Could not connect to the Plex MCP backend on port 10740."
							hint={BACKEND_DOWN_HINT}
						/>
					</div>
				) : !plexConnected ? (
					<div className="mb-6">
						<ErrorBanner
							title="Plex not connected"
							message={String(status?.message ?? status?.error ?? "Could not reach Plex server.")}
							hint={PLEX_TOKEN_HINT}
							actionHref="/settings"
							actionLabel="Open Settings → Plex"
						/>
					</div>
				) : (
					<p className="text-slate-500 mb-6 text-sm">
						{String(
							(status?.message as string | undefined) ??
								(dashboard?.server?.message as string | undefined) ??
								"Connected to Plex",
						)}
					</p>
				)}

				{/* KPI stat cards (fleet gate 1) */}
				<section
					aria-label="Library statistics"
					className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6"
				>
					<KpiCard
						testId="kpi-libraries"
						href="/libraries"
						icon={Library}
						label="Libraries"
						value={loading ? "…" : String(libCount ?? "—")}
						sub={loading ? "Loading…" : libTypeSummary}
					/>
					<KpiCard
						testId="kpi-server"
						href="/server"
						icon={Server}
						label="Plex server"
						value={loading ? "…" : plexConnected ? "Connected" : "Offline"}
						sub={loading ? "Loading…" : String(status?.message ?? "Check Settings → Plex")}
					/>
					<KpiCard
						testId="kpi-enriched"
						href="/enrichment"
						icon={Film}
						label="Enriched dossiers"
						value={loading ? "…" : enrichedCount != null ? String(enrichedCount) : "—"}
						sub={loading ? "Loading…" : "Deep dossiers cached 90 days"}
					/>
					<KpiCard
						testId="kpi-rag"
						href="/search/semantic"
						icon={Database}
						label="Semantic index"
						value={
							loading
								? "…"
								: ragAvailable
									? ragIndexed != null
										? String(ragIndexed)
										: "Ready"
									: "Not built"
						}
						sub={loading ? "Loading…" : ragPhase ? `Sync phase: ${ragPhase}` : "Run Reindex in RAG"}
					/>
					<KpiCard
						testId="kpi-taste"
						href="/taste"
						icon={Fingerprint}
						label="Taste profile"
						value={loading ? "…" : tasteBuilt ? String(tasteEvents ?? "Built") : "Not built"}
						sub={
							loading
								? "Loading…"
								: tasteBuilt
									? `${tasteEvents ?? 0} watch events scored`
									: "Rebuild from Plex history"
						}
					/>
					<KpiCard
						testId="kpi-llm"
						href="/settings"
						icon={Activity}
						label="LLM providers"
						value={loading ? "…" : llmConfigured != null ? String(llmConfigured) : "—"}
						sub={loading ? "Loading…" : "Configured providers in Settings"}
					/>
				</section>

				{/* Action buttons (fleet gate 1) */}
				<section aria-label="Quick actions" className="mb-8">
					<h2 className="text-sm uppercase tracking-wide text-slate-500 mb-3">Quick actions</h2>
					<div className="flex flex-wrap gap-2">
						{actions.map(({ href, label, icon: Icon }) => (
							<Link
								key={href + label}
								href={href}
								className="inline-flex items-center gap-2 px-4 py-2 rounded-lg glass-panel border border-slate-600/50 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
							>
								<Icon className="w-4 h-4 text-amber shrink-0" />
								{label}
							</Link>
						))}
					</div>
				</section>

				<div className="grid lg:grid-cols-2 gap-4">
					{/* Library preview */}
					<section
						aria-label="Libraries preview"
						className="rounded-xl glass-panel border border-slate-600/50 p-4"
					>
						<div className="flex items-center justify-between mb-3">
							<div className="flex items-center gap-2">
								<Layers className="w-5 h-5 text-amber shrink-0" />
								<span className="font-medium text-slate-200">Libraries</span>
							</div>
							<Link href="/libraries" className="text-sm text-amber hover:underline">
								View all
							</Link>
						</div>
						{dashboard?.libraries.items && dashboard.libraries.items.length > 0 ? (
							<ul className="space-y-2">
								{dashboard.libraries.items.slice(0, 6).map((lib) => (
									<li
										key={lib.id || lib.title}
										className="flex items-center justify-between text-sm gap-2"
									>
										<span className="text-slate-300 truncate">{lib.title}</span>
										<span className="text-slate-500 text-xs shrink-0">{lib.type}</span>
									</li>
								))}
							</ul>
						) : (
							<p className="text-sm text-slate-500">
								{loading ? "Loading libraries…" : "No libraries yet - connect Plex in Settings."}
							</p>
						)}
					</section>

					<div className="max-w-lg w-full">
						<ArrStackCard data={arrStatus} />
					</div>
				</div>
			</div>
		</main>
	);
}
