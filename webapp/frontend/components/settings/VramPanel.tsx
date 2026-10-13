"use client";

import { getLlmGpus, getLlmLoaded, unloadLlm } from "@/utils/api";
import type { GpuInfo, LoadedModel } from "@/utils/api";
import { useCallback, useEffect, useState } from "react";

function formatMb(mb: number): string {
	return mb >= 1024 ? `${(mb / 1024).toFixed(1)} GB` : `${mb} MB`;
}

const GPU_KEY = "llm_gpu";

function pickTargetGpu(gpus: GpuInfo[]): number {
	try {
		const saved = localStorage.getItem(GPU_KEY);
		if (saved != null && gpus.some((g) => g.index === Number(saved))) return Number(saved);
	} catch {}
	const secondary = gpus.find((g) => g.index > 0);
	return secondary ? secondary.index : (gpus[0]?.index ?? 0);
}

export function VramPanel() {
	const [gpus, setGpus] = useState<GpuInfo[]>([]);
	const [loaded, setLoaded] = useState<LoadedModel[]>([]);
	const [engine, setEngine] = useState(false);
	const [loading, setLoading] = useState(false);
	const [evicting, setEvicting] = useState(false);
	const [message, setMessage] = useState<string | null>(null);
	const [targetGpu, setTargetGpu] = useState<number>(0);

	const refresh = useCallback(async () => {
		setLoading(true);
		try {
			const [gpuResult, loadedResult] = await Promise.all([getLlmGpus(), getLlmLoaded()]);
			setGpus(gpuResult.gpus);
			setLoaded(loadedResult.models);
			setEngine(loadedResult.engine);
			if (gpuResult.gpus.length > 0) setTargetGpu(pickTargetGpu(gpuResult.gpus));
		} catch {
			setGpus([]);
			setLoaded([]);
			setEngine(false);
		} finally {
			setLoading(false);
		}
	}, []);

	const handleGpuChange = (index: number) => {
		setTargetGpu(index);
		try {
			localStorage.setItem(GPU_KEY, String(index));
		} catch {}
	};

	useEffect(() => {
		void refresh();
	}, [refresh]);

	const handleEvictAll = async () => {
		setEvicting(true);
		setMessage(null);
		try {
			const result = await unloadLlm();
			setMessage(
				result.evicted.length ? `Evicted: ${result.evicted.join(", ")}` : "Nothing was loaded.",
			);
			// VRAM frees asynchronously - re-read now and again shortly after.
			await refresh();
			setTimeout(() => void refresh(), 2000);
			setTimeout(() => void refresh(), 5000);
		} catch (e) {
			setMessage(e instanceof Error ? e.message : "Evict failed");
		} finally {
			setEvicting(false);
		}
	};

	if (!engine && gpus.length === 0 && !loading) {
		return null;
	}

	return (
		<div
			className="mt-4 rounded-lg border border-slate-600/50 bg-slate-900/40 p-4"
			data-testid="vram-panel"
		>
			<div className="flex items-center justify-between gap-3 mb-2">
				<span className="text-xs font-medium uppercase tracking-wide text-slate-500">
					GPU / Ollama VRAM
				</span>
				{engine && (
					<button
						type="button"
						onClick={() => void handleEvictAll()}
						disabled={evicting}
						data-testid="llm-evict-all"
						className="px-2.5 py-1 rounded-md bg-slate-700 text-slate-200 text-xs font-medium hover:bg-slate-600 disabled:opacity-50 border border-slate-600/50"
					>
						{evicting ? "Evicting..." : "Evict all"}
					</button>
				)}
			</div>

			{gpus.length > 1 && (
				<label className="flex items-center gap-2 text-xs text-slate-400 mb-2">
					Target GPU
					<select
						value={targetGpu}
						onChange={(e) => handleGpuChange(Number(e.target.value))}
						data-testid="llm-gpu-select"
						className="px-2 py-1 rounded-md bg-slate-800 border border-slate-600 text-slate-200 text-xs"
					>
						{gpus.map((gpu) => (
							<option key={gpu.index} value={gpu.index}>
								GPU {gpu.index} - {gpu.name} ({formatMb(gpu.total_mb)})
							</option>
						))}
					</select>
				</label>
			)}
			{gpus.map((gpu) => (
				<div key={gpu.index} className="text-xs text-slate-400 mb-1">
					GPU {gpu.index} ({gpu.name}): {formatMb(gpu.used_mb)} / {formatMb(gpu.total_mb)} used
					{gpus.length > 1 && gpu.index === targetGpu ? " (target)" : ""}
				</div>
			))}
			{gpus.length === 0 && (
				<p className="text-xs text-slate-500 mb-1">
					No NVIDIA GPU detected - local models will run on CPU, or use a cloud provider above.
				</p>
			)}

			{engine && (
				<div className="text-xs text-slate-400 mt-2">
					{loaded.length === 0 ? (
						<span className="text-slate-500">No models currently resident in VRAM.</span>
					) : (
						<ul className="space-y-0.5">
							{loaded.map((m) => (
								<li key={m.name}>
									{m.name} - {formatMb(m.size_vram_mb)}
								</li>
							))}
						</ul>
					)}
				</div>
			)}

			{message && <p className="text-amber text-xs mt-2">{message}</p>}
		</div>
	);
}
