"use client";

import { Terminal } from "lucide-react";
import React, { useEffect, useRef } from "react";

interface StreamingLogProps {
	logs: string[];
}

export function StreamingLog({ logs }: StreamingLogProps) {
	const scrollRef = useRef<HTMLDivElement>(null);

	useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
		}
	}, [logs]);

	return (
		<div className="glass-panel p-4 flex flex-col gap-3 h-[300px]">
			<div className="flex items-center gap-2 text-slate-400 text-xs font-mono uppercase tracking-widest">
				<Terminal className="w-3 h-3" />
				<span>Telemetry Console</span>
			</div>
			<div
				ref={scrollRef}
				className="flex-1 bg-slate-950/80 rounded border border-slate-800 p-3 font-mono text-[11px] leading-relaxed overflow-y-auto scrollbar-thin scrollbar-thumb-slate-700"
			>
				{logs.length === 0 ? (
					<div className="text-slate-700 italic">Awaiting technical signal...</div>
				) : (
					<div className="flex flex-col gap-1">
						{logs.map((log, i) => {
							const type = log.includes("[ERROR]")
								? "text-red-400"
								: log.includes("[SUCCESS]")
									? "text-emerald-400"
									: log.includes("[PROBE]")
										? "text-blue-400"
										: log.includes("[SYSTEM]")
											? "text-amber/70"
											: "text-slate-400";

							return (
								<div key={i} className={`${type} whitespace-pre-wrap`}>
									{log}
								</div>
							);
						})}
					</div>
				)}
			</div>
		</div>
	);
}
