"use client";

import {
	AlertTriangle,
	ChevronRight,
	Database,
	FileVideo,
	Hammer,
	Play,
	Search,
	Settings2,
	Terminal,
	Wrench,
} from "lucide-react";
import React, { useState, useEffect, useRef } from "react";
import { MediaProbeView } from "./media-probe-view";
import { RepairControls } from "./repair-controls";
import { StreamingLog } from "./streaming-log";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:10740";

export function RepairDashboard() {
	const [libraries, setLibraries] = useState<any[]>([]);
	const [selectedLibrary, setSelectedLibrary] = useState<any>(null);
	const [items, setItems] = useState<any[]>([]);
	const [selectedItem, setSelectedItem] = useState<any>(null);
	const [probeData, setProbeData] = useState<any>(null);
	const [logs, setLogs] = useState<string[]>([]);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	// Fetch libraries on mount
	useEffect(() => {
		fetchLibraries();
	}, []);

	async function fetchLibraries() {
		try {
			const res = await fetch(`${API_BASE}/api/libraries`);
			const data = await res.json();
			if (data.success) {
				setLibraries(data.data || []);
			}
		} catch (_err) {
			setError("Failed to connect to backend");
		}
	}

	async function fetchItems(libId: string) {
		setLoading(true);
		setError(null);
		try {
			// Use the existing movies or library browse endpoint
			const res = await fetch(`${API_BASE}/api/libraries/${libId}/items?limit=50`);
			const data = await res.json();
			if (data.success) {
				setItems(data.data || []);
			}
		} catch (_err) {
			setError("Failed to fetch library items");
		} finally {
			setLoading(false);
		}
	}

	async function handleProbe(item: any) {
		setLoading(true);
		setSelectedItem(item);
		setProbeData(null);
		addLog(`[SYSTEM] Selecting item: ${item.title}`);
		addLog(`[PROBE] Initializing ffprobe for ${item.file_path || "Plex Binary"}`);

		try {
			const res = await fetch(`${API_BASE}/api/repair/probe?media_key=${item.key}`, {
				method: "POST",
			});
			const data = await res.json();
			if (data.success) {
				setProbeData(data.data);
				addLog(`[SUCCESS] Probe complete. Found ${data.data.streams?.length || 0} streams.`);
			} else {
				setError(data.error || "Probe failed");
				addLog(`[ERROR] Probe failed: ${data.error}`);
			}
		} catch (_err) {
			setError("Probe connection error");
		} finally {
			setLoading(false);
		}
	}

	function addLog(msg: string) {
		setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
	}

	const clearSelection = () => {
		setSelectedItem(null);
		setProbeData(null);
	};

	return (
		<div className="flex flex-col gap-6 w-full animate-in fade-in duration-500">
			<div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
				{/* Navigation Column */}
				<div className="lg:col-span-4 flex flex-col gap-4">
					<div className="glass-panel p-4 flex flex-col gap-4">
						<div className="flex items-center gap-2 text-amber font-semibold">
							<Database className="w-4 h-4" />
							<span>Library Audit</span>
						</div>

						{!selectedLibrary ? (
							<div className="space-y-2">
								{libraries.map((lib) => (
									<button
										key={lib.id}
										onClick={() => {
											setSelectedLibrary(lib);
											fetchItems(lib.id);
										}}
										className="w-full flex items-center justify-between p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 transition-colors text-left"
									>
										<span>{lib.title}</span>
										<ChevronRight className="w-4 h-4 text-slate-500" />
									</button>
								))}
							</div>
						) : (
							<div className="flex flex-col gap-4">
								<button
									onClick={() => {
										setSelectedLibrary(null);
										setItems([]);
									}}
									className="text-xs text-amber hover:underline text-left"
								>
									&larr; Back to libraries
								</button>
								<div className="font-medium text-slate-300 px-1">{selectedLibrary.title}</div>
								<div className="max-h-[500px] overflow-y-auto space-y-2 pr-2">
									{loading && items.length === 0 ? (
										<div className="text-slate-500 text-sm animate-pulse p-4">
											Indexing media...
										</div>
									) : (
										items.map((item) => (
											<button
												key={item.key}
												onClick={() => handleProbe(item)}
												className={`w-full flex items-center gap-3 p-2 rounded-md text-sm text-left transition-colors ${selectedItem?.key === item.key ? "bg-amber/20 text-amber border border-amber/30" : "hover:bg-slate-700/30 text-slate-400"}`}
											>
												<FileVideo className="w-4 h-4 shrink-0" />
												<span className="truncate">{item.title}</span>
											</button>
										))
									)}
								</div>
							</div>
						)}
					</div>

					<StreamingLog logs={logs} />
				</div>

				{/* Repair Workspace Column */}
				<div className="lg:col-span-8 flex flex-col gap-6">
					{!selectedItem ? (
						<div className="glass-panel-strong h-[600px] flex flex-row items-center justify-center p-12 text-center">
							<div className="flex flex-col items-center gap-4 max-w-sm">
								<div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center border-2 border-slate-700 border-dashed">
									<Wrench className="w-8 h-8 text-slate-600" />
								</div>
								<div>
									<h3 className="text-lg font-semibold text-slate-200">No Media Selected</h3>
									<p className="text-sm text-slate-500 mt-2">
										Select a media item from your library browser to initialize the repair
										workstation and technical probe.
									</p>
								</div>
							</div>
						</div>
					) : (
						<div className="flex flex-col gap-6">
							{/* Active Media Card */}
							<div className="glass-panel-strong p-6 border-l-4 border-amber relative group">
								<div className="flex flex-col md:flex-row gap-6">
									<div className="flex-1 flex flex-col gap-2">
										<div className="flex items-center gap-2">
											<span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber text-slate-900 uppercase">
												Active Workpiece
											</span>
											{selectedItem.year && (
												<span className="text-slate-500 text-xs">{selectedItem.year}</span>
											)}
										</div>
										<h2 className="text-2xl font-bold text-white tracking-tight">
											{selectedItem.title}
										</h2>
										<code className="text-[10px] text-slate-500 bg-slate-900/50 p-1 px-2 rounded w-fit break-all">
											LOC: {selectedItem.file_path || "Database Linked"}
										</code>
									</div>
									<button
										onClick={clearSelection}
										className="h-fit text-xs text-slate-500 hover:text-white"
									>
										Release
									</button>
								</div>
							</div>

							{/* Technical Probe & Controls */}
							<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
								<MediaProbeView data={probeData} loading={loading} />
								<RepairControls
									item={selectedItem}
									probeData={probeData}
									onLog={addLog}
									onReload={() => handleProbe(selectedItem)}
								/>
							</div>
						</div>
					)}
				</div>
			</div>

			{error && (
				<div className="fixed bottom-6 right-6 p-4 rounded-lg bg-red-900/90 border border-red-500 text-white flex items-center gap-3 glass-panel-strong shadow-2xl animate-in slide-in-from-bottom-5">
					<AlertTriangle className="w-5 h-5" />
					<span>{error}</span>
					<button onClick={() => setError(null)} className="ml-4 opacity-70 hover:opacity-100">
						&times;
					</button>
				</div>
			)}
		</div>
	);
}
