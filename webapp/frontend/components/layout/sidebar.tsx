"use client";

import { checkBackendHealth, getServerStatus } from "@/utils/api";
import {
	BookOpen,
	ChevronLeft,
	ChevronRight,
	Code2,
	Database,
	FileText,
	Film,
	Fingerprint,
	GraduationCap,
	Inbox,
	LayoutDashboard,
	Library,
	MessageSquare,
	ScrollText,
	Search,
	Server,
	Settings,
	Sparkles,
	Terminal,
	Wrench,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const APP_VERSION = "v2.4.1";

const navItems = [
	{ href: "/", label: "Overview", icon: LayoutDashboard },
	{ href: "/inbox", label: "Inbox", icon: Inbox },
	{ href: "/libraries", label: "Libraries", icon: Library },
	{ href: "/movies", label: "Movies", icon: Film },
	{ href: "/repair", label: "Media Repair", icon: Wrench },
	{ href: "/search", label: "Search", icon: Search },
	{ href: "/search/semantic", label: "Semantic search", icon: Sparkles },
	{ href: "/rag", label: "RAG Management", icon: Database },
	{ href: "/enrichment", label: "Enrichment", icon: ScrollText },
	{ href: "/taste", label: "Taste", icon: Fingerprint },
	{ href: "/chat", label: "Chat", icon: MessageSquare },
	{ href: "/tools", label: "Tools", icon: Terminal },
	{ href: "/skills", label: "Skills", icon: GraduationCap },
	{ href: "/api-docs", label: "API Docs", icon: Code2 },
	{ href: "/server", label: "Server", icon: Server },
	{ href: "/logs", label: "Logs", icon: FileText },
	{ href: "/help", label: "Help", icon: BookOpen },
	{ href: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
	collapsed: boolean;
	onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
	const pathname = usePathname();
	const [backendUp, setBackendUp] = useState<boolean | null>(null);
	const [plexOk, setPlexOk] = useState<boolean | null>(null);

	useEffect(() => {
		let cancelled = false;
		const probe = async () => {
			try {
				const up = await checkBackendHealth();
				if (!cancelled) setBackendUp(up);
				if (up) {
					try {
						const s = await getServerStatus();
						if (!cancelled) setPlexOk(Boolean(s?.success));
					} catch {
						if (!cancelled) setPlexOk(false);
					}
				} else if (!cancelled) {
					setPlexOk(false);
				}
			} catch {
				if (!cancelled) {
					setBackendUp(false);
					setPlexOk(false);
				}
			}
		};
		probe();
		const t = setInterval(probe, 15000);
		return () => {
			cancelled = true;
			clearInterval(t);
		};
	}, []);

	const dotClass = backendUp === null ? "bg-slate-500" : backendUp ? "bg-green-500" : "bg-red-500";
	const statusText =
		backendUp === null
			? "Checking…"
			: backendUp
				? plexOk
					? "Plex connected"
					: "Backend up · Plex down"
				: "Backend down";
	const statusTitle = `Backend: ${backendUp === null ? "probing" : backendUp ? "up" : "down"} · Plex: ${plexOk === null ? "unknown" : plexOk ? "connected" : "down"}`;

	return (
		<aside
			className={`shrink-0 flex flex-col glass-panel-strong border-r border-slate-600/50 transition-[width] duration-200 ${collapsed ? "w-16 min-w-[4rem]" : "w-56 min-w-[14rem]"}`}
		>
			{/* Header: logo + version + collapse toggle at the TOP (fleet standard). */}
			<div
				className={`flex items-center border-b border-slate-700 px-3 py-3 ${collapsed ? "flex-col gap-2 justify-center" : "justify-between"}`}
			>
				<Link href="/" className="flex items-center gap-2 min-w-0" title="PlexMCP home">
					<Film className="w-6 h-6 text-amber shrink-0" />
					{!collapsed && (
						<span className="min-w-0 leading-tight">
							<span className="block text-sm font-semibold text-slate-100 truncate">PlexMCP</span>
							<span className="block text-[11px] text-slate-500">{APP_VERSION}</span>
						</span>
					)}
				</Link>
				<button
					type="button"
					onClick={onToggle}
					data-testid="sidebar-toggle"
					className="p-1.5 rounded-md text-slate-400 hover:text-amber hover:bg-slate-800"
					title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
					aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
				>
					{collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
				</button>
			</div>

			<nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
				{navItems.map(({ href, label, icon: Icon }) => {
					const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));
					return (
						<Link
							key={href}
							href={href}
							aria-label={label}
							className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
								isActive
									? "bg-amber/20 text-amber"
									: "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
							} ${collapsed ? "justify-center px-2" : ""}`}
							title={collapsed ? label : undefined}
						>
							<Icon className="w-5 h-5 shrink-0" />
							{!collapsed && <span>{label}</span>}
						</Link>
					);
				})}
			</nav>

			{/* Connection status indicator (fleet standard). */}
			<div
				data-testid="sidebar-connection-status"
				title={statusTitle}
				className={`flex items-center border-t border-slate-700 px-3 py-2.5 text-xs ${collapsed ? "justify-center" : "gap-2"}`}
			>
				<span className={`w-2.5 h-2.5 rounded-full shrink-0 ${dotClass}`} />
				{!collapsed && <span className="text-slate-400 truncate">{statusText}</span>}
			</div>
		</aside>
	);
}
