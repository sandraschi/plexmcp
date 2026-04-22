"use client";

import { useEffect, useState } from "react";
import { BackendStatusBanner } from "./backend-status-banner";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

const STORAGE_KEY = "plex-sidebar-collapsed";

export function AppLayout({ children }: { children: React.ReactNode }) {
	const [collapsed, setCollapsed] = useState(false);

	useEffect(() => {
		try {
			const stored = localStorage.getItem(STORAGE_KEY);
			if (stored !== null) setCollapsed(stored === "true");
		} catch {
			/* ignore */
		}
	}, []);

	const toggleCollapsed = () => {
		setCollapsed((c) => {
			const next = !c;
			try {
				localStorage.setItem(STORAGE_KEY, String(next));
			} catch {
				/* ignore quota / private mode */
			}
			return next;
		});
	};

	return (
		<div className="min-h-screen flex flex-col">
			<BackendStatusBanner />
			<Topbar />
			<div className="flex flex-1">
				<Sidebar collapsed={collapsed} onToggle={toggleCollapsed} />
				<main className="flex-1 min-w-0">{children}</main>
			</div>
		</div>
	);
}
