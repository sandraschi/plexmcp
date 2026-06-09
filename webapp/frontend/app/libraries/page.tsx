"use client";

import { ErrorBanner } from "@/components/ui/error-banner";
import { checkBackendHealth, getSettings, listLibraries } from "@/utils/api";
import { BACKEND_DOWN_HINT, PLEX_AUTH_HINT, PLEX_TOKEN_HINT } from "@/utils/config-hints";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

function librarySectionId(lib: { id?: string; key?: string }): string {
	return String(lib.id ?? lib.key ?? "");
}

type LoadState =
	| { kind: "loading" }
	| { kind: "backend_down" }
	| { kind: "no_token" }
	| { kind: "error"; message: string }
	| {
			kind: "ok";
			libraries: { key?: string; title?: string; type?: string }[];
	  };

function LibrariesPageInner() {
	const searchParams = useSearchParams();
	const activeLibraryId = searchParams?.get("library_id") ?? undefined;
	const [state, setState] = useState<LoadState>({ kind: "loading" });

	useEffect(() => {
		let cancelled = false;
		(async () => {
			setState({ kind: "loading" });
			const healthy = await checkBackendHealth();
			if (cancelled) return;
			if (!healthy) {
				setState({ kind: "backend_down" });
				return;
			}
			try {
				const settings = await getSettings();
				if (cancelled) return;
				if (!settings.plex_token_set) {
					setState({ kind: "no_token" });
					return;
				}
				const data = await listLibraries();
				if (cancelled) return;
				if (!data?.success) {
					setState({
						kind: "error",
						message: String(data?.error ?? "Could not list libraries"),
					});
					return;
				}
				setState({
					kind: "ok",
					libraries: (data.data ?? []) as {
						key?: string;
						title?: string;
						type?: string;
					}[],
				});
			} catch (e) {
				if (cancelled) return;
				const msg = e instanceof Error ? e.message : String(e);
				if (/PLEX_TOKEN/i.test(msg)) {
					setState({ kind: "no_token" });
					return;
				}
				setState({ kind: "error", message: msg });
			}
		})();
		return () => {
			cancelled = true;
		};
	}, []);

	return (
		<div className="container mx-auto p-6">
			<h1 className="text-3xl font-bold mb-6 text-slate-100">Libraries</h1>
			{state.kind === "loading" && <p className="text-slate-400">Loading libraries…</p>}
			{state.kind === "backend_down" && (
				<ErrorBanner
					title="Backend unavailable"
					message="The Plex MCP backend is not responding on port 10740."
					hint={BACKEND_DOWN_HINT}
				/>
			)}
			{state.kind === "no_token" && (
				<ErrorBanner
					title="Plex not configured"
					message="No Plex token is saved yet. Libraries need your token before they can load."
					hint={PLEX_TOKEN_HINT}
					actionHref="/settings"
					actionLabel="Open Settings → Plex"
				/>
			)}
			{state.kind === "error" && (
				<ErrorBanner
					title="Could not load libraries"
					message={state.message}
					hint={PLEX_AUTH_HINT}
					actionHref="/settings"
					actionLabel="Check Settings → Plex"
				/>
			)}
			{state.kind === "ok" && (
				<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
					{state.libraries.map(
						(lib: { id?: string; key?: string; title?: string; type?: string }, index: number) => {
							const sid = librarySectionId(lib);
							const isMovie = (lib.type ?? "").toLowerCase() === "movie";
							const href = isMovie
								? `/movies?library_id=${encodeURIComponent(sid)}`
								: `/search?library_id=${encodeURIComponent(sid)}`;
							const isActive =
								activeLibraryId != null && activeLibraryId !== "" && activeLibraryId === sid;
							return (
								<Link
									key={sid || `lib-${index}`}
									href={href}
									className={`relative block p-6 rounded-xl glass-panel border transition-colors ${
										isActive
											? "border-amber/50 ring-1 ring-amber/30"
											: "border-slate-600/50 hover:border-amber/40"
									}`}
								>
									{isActive && (
										<span className="absolute top-3 right-3 text-xs font-semibold uppercase tracking-wide px-2 py-0.5 rounded-md bg-amber/20 text-amber border border-amber/40">
											Active
										</span>
									)}
									<p className="text-xl font-semibold text-slate-100 pr-16">
										{lib.title ?? "Library"}
									</p>
									<p className="text-sm text-slate-400">{lib.type ?? ""}</p>
								</Link>
							);
						},
					)}
				</div>
			)}
		</div>
	);
}

export default function LibrariesPage() {
	return (
		<Suspense
			fallback={
				<div className="container mx-auto p-6">
					<p className="text-slate-400">Loading…</p>
				</div>
			}
		>
			<LibrariesPageInner />
		</Suspense>
	);
}
