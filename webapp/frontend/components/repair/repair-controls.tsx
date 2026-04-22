"use client";

import {
	Clock,
	Download,
	Hammer,
	Languages,
	Monitor,
	RefreshCw,
	Settings2,
	Square,
	Volume2,
} from "lucide-react";
import React, { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:10740";

interface RepairControlsProps {
	item: any;
	probeData: any;
	onLog: (msg: string) => void;
	onReload: () => void;
}

export function RepairControls({ item, probeData, onLog, onReload }: RepairControlsProps) {
	const [audioOffset, setAudioOffset] = useState<string>("0.5");
	const [subOffset, setSubOffset] = useState<string>("0.5");
	const [targetAspect, setTargetAspect] = useState<string>("16:9");
	const [reencode, setReencode] = useState(false);
	const [pending, setPending] = useState(false);

	async function execute(operation: string, params: any) {
		if (pending) return;
		setPending(true);
		onLog(`[REPAIR] Starting ${operation} operation...`);

		try {
			const res = await fetch(`${API_BASE}/api/repair/execute`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					operation,
					media_key: item.key,
					params,
				}),
			});
			const data = await res.json();
			if (data.success) {
				onLog(`[SUCCESS] ${operation} complete. Output: ${data.message || "File updated."}`);
				onReload(); // Refresh probe to show changes
			} else {
				onLog(`[ERROR] ${operation} failed: ${data.error}`);
			}
		} catch (_err) {
			onLog(`[ERROR] Connection failure during ${operation}`);
		} finally {
			setPending(false);
		}
	}

	const subStreams = probeData?.streams?.filter((s: any) => s.codec_type === "subtitle") || [];

	return (
		<div className="flex flex-col gap-4">
			{/* Audio Sync Tool */}
			<div className="glass-panel p-4 flex flex-col gap-3 group relative">
				<div className="flex items-center gap-2 text-slate-300 font-semibold text-sm">
					<Volume2 className="w-4 h-4 text-emerald-400" />
					<span>Audio Signal Synchronization</span>
				</div>
				<div className="flex items-center gap-3">
					<div className="flex-1 flex gap-2">
						<button
							onClick={() => setAudioOffset("-0.5")}
							className="px-2 py-1 bg-slate-800 rounded text-[10px] hover:bg-slate-700 transition-colors"
						>
							-0.5s
						</button>
						<input
							type="text"
							value={audioOffset}
							onChange={(e) => setAudioOffset(e.target.value)}
							className="flex-1 bg-slate-900 border border-slate-700 rounded px-3 py-1 text-sm font-mono text-center text-emerald-400"
							placeholder="0.0"
						/>
						<button
							onClick={() => setAudioOffset("0.5")}
							className="px-2 py-1 bg-slate-800 rounded text-[10px] hover:bg-slate-700 transition-colors"
						>
							+0.5s
						</button>
					</div>
					<button
						disabled={pending}
						onClick={() =>
							execute("sync_audio", { offset_seconds: Number.parseFloat(audioOffset) })
						}
						className="p-2 rounded bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/40 border border-emerald-500/30 transition-all disabled:opacity-50"
						title="Shift Audio"
					>
						<RefreshCw className={`w-4 h-4 ${pending ? "animate-spin" : ""}`} />
					</button>
				</div>
				<p className="text-[10px] text-slate-500 mt-1 italic">
					Positive for delayed audio, negative for early audio.
				</p>
			</div>

			{/* Subtitle Sync Tool */}
			<div className="glass-panel p-4 flex flex-col gap-3">
				<div className="flex items-center gap-2 text-slate-300 font-semibold text-sm">
					<Languages className="w-4 h-4 text-purple-400" />
					<span>Subtitle Drift Correction</span>
				</div>
				<div className="flex items-center gap-3">
					<input
						type="text"
						value={subOffset}
						onChange={(e) => setSubOffset(e.target.value)}
						className="w-24 bg-slate-900 border border-slate-700 rounded px-3 py-1 text-sm font-mono text-center text-purple-400"
						placeholder="0.0"
					/>
					<button
						disabled={pending}
						onClick={() =>
							execute("sync_subtitles", { offset_seconds: Number.parseFloat(subOffset) })
						}
						className="flex-1 p-2 rounded bg-purple-500/20 text-purple-400 hover:bg-purple-500/40 border border-purple-500/30 transition-all text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2"
					>
						<Hammer className="w-3 h-3" />
						Repair All Tracks
					</button>
				</div>
			</div>

			{/* Aspect Ratio Tool */}
			<div className="glass-panel p-4 flex flex-col gap-3">
				<div className="flex items-center gap-2 text-slate-300 font-semibold text-sm">
					<Monitor className="w-4 h-4 text-amber" />
					<span>Geometry Reconstruction (DAR)</span>
				</div>
				<div className="flex flex-wrap gap-2">
					{["16:9", "4:3", "2.35:1", "1.85:1"].map((ratio) => (
						<button
							key={ratio}
							onClick={() => setTargetAspect(ratio)}
							className={`px-3 py-1 rounded text-[10px] font-bold border transition-all ${targetAspect === ratio ? "bg-amber text-slate-900 border-amber" : "bg-slate-800 border-slate-700 text-slate-400"}`}
						>
							{ratio}
						</button>
					))}
				</div>
				<div className="flex items-center gap-3 mt-1">
					<label className="flex items-center gap-2 cursor-pointer">
						<input
							type="checkbox"
							checked={reencode}
							onChange={(e) => setReencode(e.target.checked)}
							className="rounded bg-slate-800 border-slate-700 text-amber"
						/>
						<span className="text-[10px] text-slate-400">Force Re-encode (Slow)</span>
					</label>
					<button
						disabled={pending}
						onClick={() => execute("set_aspect", { aspect_ratio: targetAspect, reencode })}
						className="flex-1 p-2 rounded bg-amber/20 text-amber hover:bg-amber/40 border border-amber/30 transition-all text-xs font-bold uppercase"
					>
						Fix Ratio
					</button>
				</div>
			</div>

			{/* Extraction Hub */}
			{subStreams.length > 0 && (
				<div className="glass-panel p-4 flex flex-col gap-3">
					<div className="flex items-center gap-2 text-slate-300 font-semibold text-sm">
						<Download className="w-4 h-4 text-blue-400" />
						<span>Digital Extraction (Sidecars)</span>
					</div>
					<div className="flex flex-col gap-2 max-h-[150px] overflow-y-auto pr-1">
						{subStreams.map((s: any) => (
							<div
								key={s.index}
								className="flex items-center justify-between p-2 rounded bg-slate-900/50 border border-slate-800/50"
							>
								<div className="flex flex-col">
									<span className="text-[10px] text-slate-300">
										Stream #{s.index} ({s.codec_name})
									</span>
									<span className="text-[9px] text-slate-500 uppercase font-bold">
										{s.tags?.language || "und"}
									</span>
								</div>
								<button
									disabled={pending}
									onClick={() => execute("extract_subtitles", { stream_index: s.index })}
									className="px-2 py-1 rounded-sm bg-blue-500/20 text-blue-400 hover:bg-blue-500/40 text-[9px] font-bold uppercase transition-all"
								>
									Extract
								</button>
							</div>
						))}
					</div>
				</div>
			)}
		</div>
	);
}
