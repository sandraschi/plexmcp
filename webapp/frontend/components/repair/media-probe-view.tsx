"use client";

import { Activity, Box, Info, Languages, Music, Type } from "lucide-react";
import React from "react";

function parseFrameRate(fraction: string | undefined): number {
	if (!fraction) return 0;
	const parts = fraction.split("/");
	if (parts.length === 2) {
		const num = Number(parts[0]);
		const den = Number(parts[1]);
		if (den !== 0 && Number.isFinite(num) && Number.isFinite(den)) {
			return num / den;
		}
	}
	const n = Number(fraction);
	return Number.isFinite(n) ? n : 0;
}

interface MediaProbeViewProps {
	data: any;
	loading: boolean;
}

export function MediaProbeView({ data, loading }: MediaProbeViewProps) {
	if (loading && !data) {
		return (
			<div className="glass-panel p-6 flex flex-col gap-4 animate-pulse">
				<div className="h-4 w-1/3 bg-slate-700 rounded" />
				<div className="space-y-3">
					<div className="h-10 bg-slate-800 rounded" />
					<div className="h-10 bg-slate-800 rounded" />
					<div className="h-10 bg-slate-800 rounded" />
				</div>
			</div>
		);
	}

	if (!data) return null;

	return (
		<div className="glass-panel p-4 flex flex-col gap-4">
			<div className="flex items-center justify-between border-b border-slate-700 pb-2 mb-2">
				<div className="flex items-center gap-2 text-slate-300 font-semibold">
					<Info className="w-4 h-4 text-amber" />
					<span>Technical Blueprint</span>
				</div>
				<div className="text-[10px] text-slate-500 font-mono">
					{data.format?.format_name?.toUpperCase() || "UNKNOWN"}
				</div>
			</div>

			<div className="flex flex-col gap-3 overflow-y-auto max-h-[400px] pr-2 scrollbar-thin">
				{data.streams?.map((stream: any, idx: number) => {
					const isVideo = stream.codec_type === "video";
					const isAudio = stream.codec_type === "audio";
					const isSubtitle = stream.codec_type === "subtitle";

					return (
						<div
							key={idx}
							className={`p-3 rounded border border-slate-700/50 bg-slate-900/30 flex flex-col gap-2 transition-all hover:bg-slate-800/40 ${isVideo ? "border-l-2 border-l-blue-500/50" : isAudio ? "border-l-2 border-l-emerald-500/50" : "border-l-2 border-l-purple-500/50"}`}
						>
							<div className="flex items-center justify-between">
								<div className="flex items-center gap-2">
									<span className="text-[10px] font-bold text-slate-500 w-4">#{stream.index}</span>
									<div className="flex items-center gap-1.5 px-1.5 py-0.5 rounded-sm bg-slate-800 text-[10px] text-slate-300 font-mono">
										{isVideo && <Box className="w-3 h-3 text-blue-400" />}
										{isAudio && <Music className="w-3 h-3 text-emerald-400" />}
										{isSubtitle && <Languages className="w-3 h-3 text-purple-400" />}
										{stream.codec_name?.toUpperCase()}
									</div>
									{stream.tags?.language && (
										<span className="text-[10px] text-slate-500 uppercase font-bold">
											{stream.tags.language}
										</span>
									)}
								</div>
								{stream.tags?.title && (
									<span className="text-[10px] text-slate-600 truncate max-w-[120px]">
										{stream.tags.title}
									</span>
								)}
							</div>

							<div className="grid grid-cols-2 gap-2 text-[10px] text-slate-500">
								{isVideo && (
									<>
										<div>
											Res: {stream.width}x{stream.height}
										</div>
										<div>FPS: {parseFrameRate(stream.r_frame_rate).toFixed(2)}</div>
										<div>DAR: {stream.display_aspect_ratio || "N/A"}</div>
										<div>PixFmt: {stream.pix_fmt}</div>
									</>
								)}
								{isAudio && (
									<>
										<div>
											Ch: {stream.channels} ({stream.channel_layout})
										</div>
										<div>Rate: {stream.sample_rate}Hz</div>
									</>
								)}
							</div>
						</div>
					);
				})}
			</div>

			<div className="mt-auto pt-4 border-t border-slate-800 text-[10px]">
				<div className="flex items-center justify-between text-slate-600">
					<span>Bitrate: {(data.format?.bit_rate / 1000).toFixed(0)} kbps</span>
					<span>Size: {(data.format?.size / (1024 * 1024)).toFixed(2)} MB</span>
				</div>
			</div>
		</div>
	);
}
