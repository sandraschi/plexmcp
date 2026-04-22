import type { ArrServiceStatus, ArrStackResponse } from "@/utils/api";
import { Layers } from "lucide-react";
import Link from "next/link";

function Row({ label, s }: { label: string; s: ArrServiceStatus }) {
	if (!s.configured) {
		return (
			<div className="flex justify-between text-sm text-slate-500">
				<span>{label}</span>
				<span>not configured</span>
			</div>
		);
	}
	if (!s.reachable) {
		return (
			<div className="flex justify-between text-sm gap-2">
				<span className="text-slate-300">{label}</span>
				<span className="text-red-400 truncate max-w-[12rem]" title={s.error ?? ""}>
					unreachable
				</span>
			</div>
		);
	}
	const q = s.queue_count != null ? `${s.queue_count} in queue` : "queue ?";
	return (
		<div className="flex justify-between text-sm gap-2">
			<span className="text-slate-300">{label}</span>
			<span className="text-slate-400 text-right">
				v{s.version ?? "?"} · {q}
			</span>
		</div>
	);
}

export function ArrStackCard({ data }: { data: ArrStackResponse | null }) {
	if (data === null) {
		return (
			<div className="rounded-xl glass-panel border border-slate-600/50 p-4 text-sm text-slate-500">
				*arr status unavailable (backend offline).
			</div>
		);
	}

	if (!data.any_configured) {
		return (
			<div className="rounded-xl glass-panel border border-slate-600/50 p-4">
				<div className="flex items-center gap-2 mb-2">
					<Layers className="w-5 h-5 text-amber shrink-0" />
					<span className="font-medium text-slate-200">*arr stack</span>
				</div>
				<p className="text-sm text-slate-500 mb-2">
					Optional: if your *arr apps run in Docker (media stack), add each service&apos;s base URL
					and API key in Settings. Same snapshot is available to the MCP{" "}
					<code className="text-amber text-xs">arr_stack</code> tool.
				</p>
				<Link href="/settings" className="text-sm text-amber hover:underline">
					Open settings
				</Link>
			</div>
		);
	}

	return (
		<div className="rounded-xl glass-panel border border-slate-600/50 p-4">
			<div className="flex items-center gap-2 mb-3">
				<Layers className="w-5 h-5 text-amber shrink-0" />
				<span className="font-medium text-slate-200">*arr stack</span>
			</div>
			<div className="space-y-2">
				<Row label="Radarr" s={data.radarr} />
				<Row label="Sonarr" s={data.sonarr} />
				<Row label="Lidarr" s={data.lidarr} />
			</div>
			<p className="text-xs text-slate-600 mt-3">
				Read-only HTTP checks from the webapp backend to your stack (Docker host, LAN, or proxy
				URL). Use each app&apos;s UI to manage downloads.
			</p>
		</div>
	);
}
