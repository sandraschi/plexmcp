"use client";

import { ArrStackCard } from "@/components/overview/arr-stack-card";
import { ErrorBanner } from "@/components/ui/error-banner";
import { type ArrStackResponse, getArrStackStatus, getServerStatus } from "@/utils/api";
import { Library, Search, Server } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const BACKEND_HINT =
	"Set PLEX_TOKEN in webapp/backend/.env. Run: cd webapp; powershell -ExecutionPolicy Bypass -File .\\start.ps1";

export default function Home() {
	const [status, setStatus] = useState<{
		success?: boolean;
		message?: string;
		[key: string]: unknown;
	} | null>(null);
	const [arrStatus, setArrStatus] = useState<ArrStackResponse | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		let cancelled = false;
		(async () => {
			try {
				const s = await getServerStatus();
				if (!cancelled) setStatus(s);
			} catch {
				if (!cancelled) setStatus(null);
			}
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
						message="Could not connect to PlexMCP backend. Ensure backend is running and PLEX_TOKEN is set."
						hint={BACKEND_HINT}
					/>
				) : status.success ? (
					<p className="text-slate-500 mb-6">{String(status.message ?? "Connected to Plex")}</p>
				) : (
					<p className="text-amber/80 mb-6">
						{String(status.message ?? status.error ?? "Check PLEX_TOKEN")}
					</p>
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
