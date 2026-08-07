"use client";

import { API_BASE } from "@/utils/api";
import { ChevronDown, Container, ExternalLink, FileText, Film, HelpCircle, Moon, Sun } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { HelpModal } from "./help-modal";
import { LoggerModal } from "./logger-modal";

// EXPERIMENTAL light mode (invert hack). Not fleet standard — see globals.css.
// Toggling `.dark` off the root flips the invert filter; persisted so the
// choice survives reloads. Delete this + the CSS block to revert.
const THEME_KEY = "plex-light-mode";

function useExperimentalTheme() {
	const [light, setLight] = useState(() => {
		if (typeof window === "undefined") return false;
		try {
			return localStorage.getItem(THEME_KEY) === "1";
		} catch {
			return false;
		}
	});

	useEffect(() => {
		document.documentElement.classList.toggle("dark", !light);
		try {
			localStorage.setItem(THEME_KEY, light ? "1" : "0");
		} catch {
			// ignore storage errors
		}
	}, [light]);

	return { light, toggle: () => setLight((v) => !v) };
}

const WEBAPP_ZOO: { label: string; url: string; port?: number }[] = [
	{ label: "PlexMCP", url: "http://127.0.0.1:10741", port: 10741 },
	{ label: "Advanced Memory", url: "http://127.0.0.1:10704", port: 10704 },
	{ label: "Calibre MCP", url: "http://127.0.0.1:10721", port: 10721 },
	{ label: "Robotics MCP", url: "http://127.0.0.1:10706", port: 10706 },
	{ label: "MyAI Dashboard", url: "http://127.0.0.1:3060", port: 3060 },
	{ label: "Virtualization MCP", url: "http://127.0.0.1:10700", port: 10700 },
	{ label: "Database Ops MCP", url: "http://127.0.0.1:10708", port: 10708 },
	{ label: "Avatar MCP", url: "http://127.0.0.1:10710", port: 10710 },
	{ label: "VRChat MCP", url: "http://127.0.0.1:10712", port: 10712 },
	{ label: "Ring MCP", url: "http://127.0.0.1:10728", port: 10728 },
	{ label: "MyAI Calibre Plus", url: "http://127.0.0.1:10734", port: 10734 },
	{ label: "MyAI Plex Plus", url: "http://127.0.0.1:10760", port: 10760 },
	{ label: "Games App", url: "http://127.0.0.1:10726", port: 10726 },
];

/** Naive list of Docker (or similar) containers with a web UI port. Later: standardize frontend vs infra. */
const CONTAINER_LINKS: { label: string; url: string; port: number }[] = [
	{ label: "Portainer", url: "http://127.0.0.1:9001", port: 9001 },
	{ label: "Traefik", url: "http://127.0.0.1:8080", port: 8080 },
	{ label: "Grafana", url: "http://127.0.0.1:3100", port: 3100 },
	{ label: "MyAI Dashboard", url: "http://127.0.0.1:3060", port: 3060 },
	{ label: "MyAI Calibre Plus", url: "http://127.0.0.1:10734", port: 10734 },
	{ label: "MyAI Plex Plus", url: "http://127.0.0.1:10760", port: 10760 },
	{ label: "MyAI Document Viewer", url: "http://127.0.0.1:10744", port: 10744 },
	{ label: "MyAI Future You", url: "http://127.0.0.1:10746", port: 10746 },
	{ label: "MyAI Immich", url: "http://127.0.0.1:10756", port: 10756 },
	{ label: "MyAI Voice AI", url: "http://127.0.0.1:10778", port: 10778 },
	{ label: "MyAI Traefik", url: "http://127.0.0.1:10790", port: 10790 },
];

async function checkUrlUp(url: string, timeoutMs = 2500): Promise<boolean> {
	try {
		const c = new AbortController();
		const t = setTimeout(() => c.abort(), timeoutMs);
		const r = await fetch(url, {
			method: "GET",
			signal: c.signal,
			cache: "no-store",
		});
		clearTimeout(t);
		return r.ok;
	} catch {
		return false;
	}
}

interface LaunchModalState {
	label: string;
	url: string;
	status: "starting" | "done" | "error";
	error?: string;
}

export function Topbar() {
	const [showHelp, setShowHelp] = useState(false);
	const [showLogger, setShowLogger] = useState(false);
	const [showZoo, setShowZoo] = useState(false);
	const [showContainers, setShowContainers] = useState(false);
	const [launchModal, setLaunchModal] = useState<LaunchModalState | null>(null);
	const zooRef = useRef<HTMLDivElement>(null);
	const containersRef = useRef<HTMLDivElement>(null);
	const { light, toggle } = useExperimentalTheme();

	useEffect(() => {
		if (!showZoo) return;
		const close = (e: MouseEvent) => {
			if (zooRef.current && !zooRef.current.contains(e.target as Node)) setShowZoo(false);
		};
		document.addEventListener("click", close);
		return () => document.removeEventListener("click", close);
	}, [showZoo]);

	useEffect(() => {
		if (!showContainers) return;
		const close = (e: MouseEvent) => {
			if (containersRef.current && !containersRef.current.contains(e.target as Node))
				setShowContainers(false);
		};
		document.addEventListener("click", close);
		return () => document.removeEventListener("click", close);
	}, [showContainers]);

	const handleContainerClick = (item: { label: string; url: string }) => {
		setShowContainers(false);
		window.open(item.url, "_blank", "noopener,noreferrer");
	};

	const handleWebappClick = async (app: {
		label: string;
		url: string;
		port?: number;
	}) => {
		setShowZoo(false);
		const url = app.url;
		const up = await checkUrlUp(url);
		if (up) {
			window.open(url, "_blank", "noopener,noreferrer");
			return;
		}
		if (app.port == null) {
			window.open(url, "_blank", "noopener,noreferrer");
			return;
		}
		setLaunchModal({ label: app.label, url, status: "starting" });
		try {
			const r = await fetch(`${API_BASE}/api/webapp-launch`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ port: app.port }),
			});
			const data = await r.json().catch(() => ({}));
			if (!r.ok) {
				setLaunchModal((m) =>
					m
						? {
								...m,
								status: "error",
								error: data.detail ?? data.error ?? `HTTP ${r.status}`,
							}
						: null,
				);
				return;
			}
			if (data.error) {
				setLaunchModal((m) => (m ? { ...m, status: "error", error: data.error } : null));
				return;
			}
			setLaunchModal((m) => (m ? { ...m, status: "done" } : null));
			window.open(url, "_blank", "noopener,noreferrer");
			setTimeout(() => setLaunchModal(null), 1500);
		} catch (e) {
			setLaunchModal((m) =>
				m
					? {
							...m,
							status: "error",
							error: e instanceof Error ? e.message : "Request failed",
						}
					: null,
			);
		}
	};

	return (
		<>
			<header className="sticky top-0 z-50 border-b border-slate-700/50 glass-panel-strong">
				<div className="container mx-auto px-4 h-14 flex items-center justify-between gap-4">
					<Link
						href="/"
						className="text-xl font-semibold text-amber shrink-0 flex items-center gap-2"
					>
						<Film className="w-6 h-6" />
						PlexMCP
					</Link>
					<div className="flex items-center gap-2">
						<button
							type="button"
							onClick={toggle}
							className="p-2 rounded-md text-slate-400 hover:bg-slate-700/50 hover:text-amber"
							title={light ? "Switch to dark (experimental light mode)" : "Switch to light (experimental, ugly)"}
							aria-label="Toggle light mode (experimental)"
						>
							{light ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
						</button>
						<div className="relative" ref={zooRef}>
							<button
								type="button"
								onClick={() => setShowZoo(!showZoo)}
								className="flex items-center gap-1.5 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-700/50 hover:text-amber text-sm"
								title="Jump to other webapps"
							>
								<ExternalLink className="w-4 h-4" />
								<span className="hidden sm:inline">Webapps</span>
								<ChevronDown
									className={`w-4 h-4 transition-transform ${showZoo ? "rotate-180" : ""}`}
								/>
							</button>
							{showZoo && (
								<div className="absolute right-0 mt-1 py-1 w-56 max-h-80 overflow-auto rounded-lg glass-panel border border-slate-600/50 shadow-xl z-50">
									{WEBAPP_ZOO.map((app) => (
										<button
											key={app.url}
											type="button"
											onClick={() => handleWebappClick(app)}
											className="block w-full text-left px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/80 hover:text-amber"
										>
											{app.label}
											{app.port != null && (
												<span className="text-slate-500 text-xs ml-1">:{app.port}</span>
											)}
										</button>
									))}
								</div>
							)}
						</div>
						<div className="relative" ref={containersRef}>
							<button
								type="button"
								onClick={() => setShowContainers(!showContainers)}
								className="flex items-center gap-1.5 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-700/50 hover:text-amber text-sm"
								title="Jump to container UIs (Docker, etc.)"
							>
								<Container className="w-4 h-4" />
								<span className="hidden sm:inline">Containers</span>
								<ChevronDown
									className={`w-4 h-4 transition-transform ${showContainers ? "rotate-180" : ""}`}
								/>
							</button>
							{showContainers && (
								<div className="absolute right-0 mt-1 py-1 w-56 max-h-80 overflow-auto rounded-lg glass-panel border border-slate-600/50 shadow-xl z-50">
									{CONTAINER_LINKS.map((item) => (
										<button
											key={item.url}
											type="button"
											onClick={() => handleContainerClick(item)}
											className="block w-full text-left px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/80 hover:text-amber"
										>
											{item.label}
											<span className="text-slate-500 text-xs ml-1">:{item.port}</span>
										</button>
									))}
								</div>
							)}
						</div>
						<button
							type="button"
							onClick={() => setShowHelp(true)}
							className="p-2 rounded-md text-slate-400 hover:bg-slate-700/50 hover:text-amber"
							title="Help"
						>
							<HelpCircle className="w-5 h-5" />
						</button>
						<button
							type="button"
							onClick={() => setShowLogger(true)}
							className="p-2 rounded-md text-slate-400 hover:bg-slate-700/50 hover:text-amber"
							title="Logs"
						>
							<FileText className="w-5 h-5" />
						</button>
					</div>
				</div>
			</header>
			{showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
			{showLogger && <LoggerModal onClose={() => setShowLogger(false)} />}
			{launchModal && (
				<dialog
					open
					className="fixed inset-0 z-[100] m-0 flex h-full w-full max-h-none max-w-none items-center justify-center border-0 bg-black/50 p-0"
				>
					<div className="rounded-lg glass-panel border border-slate-600/50 shadow-xl px-6 py-4 max-w-sm text-center">
						{launchModal.status === "starting" && (
							<>
								<p className="text-slate-200 font-medium">Starting {launchModal.label}</p>
								<p className="text-slate-400 text-sm mt-1">Please wait...</p>
							</>
						)}
						{launchModal.status === "done" && (
							<p className="text-amber">Opened {launchModal.label}</p>
						)}
						{launchModal.status === "error" && (
							<>
								<p className="text-red-400 font-medium">Could not start {launchModal.label}</p>
								<p className="text-slate-400 text-sm mt-1">{launchModal.error}</p>
								<p className="text-slate-500 text-xs mt-2">
									Run the start script in the repo manually.
								</p>
								<button
									type="button"
									onClick={() => setLaunchModal(null)}
									className="mt-3 px-4 py-2 rounded bg-slate-700 text-slate-200 hover:bg-slate-600 text-sm"
								>
									Close
								</button>
							</>
						)}
					</div>
				</dialog>
			)}
		</>
	);
}
