"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import { getServerStatus, listLibraries } from "@/utils/api";
import { BACKEND_DOWN_HINT } from "@/utils/config-hints";
import { listClients } from "@/utils/playback";
import { Inbox, MonitorPlay, Search } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Client = { name?: string; product?: string; state?: string; [k: string]: unknown };
type Library = { id?: string; key?: string; title?: string; name?: string; type?: string };

export default function InboxPage() {
	const [clients, setClients] = useState<Client[] | null>(null);
	const [libraries, setLibraries] = useState<Library[] | null>(null);
	const [serverOk, setServerOk] = useState<boolean | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [filter, setFilter] = useState("");

	const load = async () => {
		setLoading(true);
		setError(null);
		try {
			const [s, libs, cls] = await Promise.allSettled([
				getServerStatus(),
				listLibraries(),
				listClients(),
			]);
			if (s.status === "fulfilled") setServerOk(Boolean(s.value?.success));
			else setServerOk(false);
			if (libs.status === "fulfilled") {
				const v = libs.value;
				setLibraries(Array.isArray(v) ? v : (v?.libraries ?? v?.data ?? []));
			}
			if (cls.status === "fulfilled") {
				const v = cls.value;
				setClients(Array.isArray(v) ? v : (v?.clients ?? v?.data ?? []));
			}
		} catch (e) {
			setError(e instanceof Error ? e.message : String(e));
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		load();
	}, []);

	const filteredLibraries = useMemo(() => {
		if (!libraries) return null;
		const q = filter.trim().toLowerCase();
		if (!q) return libraries;
		return libraries.filter((l) =>
			`${l.title ?? l.name ?? ""} ${l.type ?? ""}`.toLowerCase().includes(q),
		);
	}, [libraries, filter]);

	const playing = (clients ?? []).filter((c) =>
		["playing", "paused", "buffering"].includes(String(c.state ?? "").toLowerCase()),
	);

	return (
		<div className="container mx-auto p-6 max-w-6xl" data-testid="inbox-page">
			<div className="flex items-start gap-3 mb-2">
				<Inbox className="w-7 h-7 text-amber shrink-0 mt-0.5" />
				<div>
					<h1 className="text-3xl font-bold text-slate-100">Inbox</h1>
					<p className="text-slate-500 mt-1 text-sm">
						What needs attention: active playback plus your libraries at a glance.
					</p>
				</div>
			</div>

			{loading ? (
				<p className="text-slate-500 mt-6" data-testid="inbox-loading">
					Loading inbox…
				</p>
			) : error ? (
				<div className="mt-6" data-testid="inbox-error">
					<ErrorBanner title="Inbox unavailable" message={error} hint={BACKEND_DOWN_HINT} />
					<button
						type="button"
						onClick={load}
						className="mt-3 px-4 py-2 rounded-lg border border-slate-600 text-sm text-slate-200 hover:border-amber/40 hover:text-amber transition-colors"
					>
						Retry
					</button>
				</div>
			) : (
				<div className="mt-6 space-y-4">
					<section
						aria-label="Active playback"
						className="rounded-xl glass-panel border border-slate-600/50 p-4"
					>
						<div className="flex items-center gap-2 mb-3">
							<MonitorPlay className="w-5 h-5 text-amber shrink-0" />
							<span className="font-medium text-slate-200">Now playing</span>
							<span className="text-xs text-slate-500 ml-auto" data-testid="inbox-session-count">
								{playing.length} active session{playing.length === 1 ? "" : "s"}
							</span>
						</div>
						{playing.length > 0 ? (
							<ul className="space-y-2">
								{playing.map((c, i) => (
									<li
										key={String(c.name ?? c.product ?? i)}
										data-testid={`inbox-session-${i}`}
										className="flex items-center justify-between text-sm gap-2"
									>
										<span className="text-slate-300 truncate">
											{String(c.name ?? c.product ?? "Unknown client")}
										</span>
										<span className="text-xs text-amber shrink-0">{String(c.state ?? "")}</span>
									</li>
								))}
							</ul>
						) : (
							<p className="text-sm text-slate-500" data-testid="inbox-empty">
								Nothing playing right now.
								{serverOk === false && " Plex itself looks unreachable — check Settings → Plex."}
							</p>
						)}
					</section>

					<section
						aria-label="Libraries"
						className="rounded-xl glass-panel border border-slate-600/50 p-4"
					>
						<div className="flex items-center gap-2 mb-3 flex-wrap">
							<span className="font-medium text-slate-200">Libraries</span>
							<span className="text-xs text-slate-500" data-testid="inbox-library-count">
								{filteredLibraries?.length ?? 0} shown
							</span>
							<label className="relative ml-auto">
								<Search className="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
								<input
									type="search"
									value={filter}
									onChange={(e) => setFilter(e.target.value)}
									placeholder="Filter libraries…"
									data-testid="inbox-filter"
									className="pl-8 pr-3 py-1.5 text-sm rounded-lg bg-slate-800 border border-slate-600/50 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-amber/40"
								/>
							</label>
						</div>
						{filteredLibraries && filteredLibraries.length > 0 ? (
							<ul className="grid sm:grid-cols-2 gap-2">
								{filteredLibraries.map((l) => {
									const id = String(l.id ?? l.key ?? l.title ?? l.name ?? "");
									return (
										<li key={id}>
											<Link
												href={`/libraries/${encodeURIComponent(id)}`}
												className="flex items-center justify-between gap-2 px-3 py-2 rounded-lg border border-slate-600/50 text-sm text-slate-300 hover:border-amber/40 hover:text-amber transition-colors"
											>
												<span className="truncate">{String(l.title ?? l.name ?? id)}</span>
												<span className="text-xs text-slate-500 shrink-0">
													{String(l.type ?? "")}
												</span>
											</Link>
										</li>
									);
								})}
							</ul>
						) : (
							<p className="text-sm text-slate-500">
								{filter
									? "No libraries match this filter."
									: "No libraries yet — connect Plex in Settings."}
							</p>
						)}
					</section>
				</div>
			)}
		</div>
	);
}
