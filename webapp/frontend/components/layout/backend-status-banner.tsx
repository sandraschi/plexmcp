"use client";

import { API_BASE } from "@/utils/api";
import { useCallback, useEffect, useState } from "react";

const POLL_MS = 20000;

/**
 * Shows a full-width banner when the FastAPI backend (proxied at /api/health) is unreachable.
 */
export function BackendStatusBanner() {
	const [ok, setOk] = useState<boolean | null>(null);

	const check = useCallback(async () => {
		try {
			const res = await fetch(`${API_BASE}/health`, {
				cache: "no-store",
				method: "GET",
			});
			setOk(res.ok);
		} catch {
			setOk(false);
		}
	}, []);

	useEffect(() => {
		void check();
		const id = setInterval(() => void check(), POLL_MS);
		return () => clearInterval(id);
	}, [check]);

	if (ok === null || ok === true) {
		return null;
	}

	return (
		<output
			aria-live="polite"
			className="block w-full border-b border-amber-800/60 bg-amber-950/90 px-4 py-2 text-center text-sm text-amber-100"
		>
			<strong className="font-semibold">Backend offline.</strong> Start the
			FastAPI server on port <strong>10740</strong> (e.g.{" "}
			<code className="rounded bg-slate-900/80 px-1">webapp/start.ps1</code> or{" "}
			<code className="rounded bg-slate-900/80 px-1">uvicorn</code>
			). Search, settings, and API-driven features will fail until the API is
			up.
		</output>
	);
}
