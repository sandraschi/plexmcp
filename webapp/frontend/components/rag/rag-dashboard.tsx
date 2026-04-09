"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Database, 
  Brain, 
  RefreshCcw, 
  Activity, 
  LayoutGrid, 
  FileText, 
  AlertCircle,
  CheckCircle2,
  Clock,
  Terminal,
  Zap
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:10740";

export function RAGDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [syncStatus, setSyncStatus] = useState<any>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  // Initial stats fetch
  useEffect(() => {
    fetchStats();
    // Poll sync status if idling or syncing
    const interval = setInterval(fetchSyncStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  async function fetchStats() {
    try {
      const res = await fetch(`${API_BASE}/api/rag/stats`);
      const data = await res.json();
      if (data.success) {
        setStats(data.data);
      }
    } catch (err) {
      console.error("Failed to fetch RAG stats");
    }
  }

  async function fetchSyncStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/rag/sync/status`);
      const data = await res.json();
      setSyncStatus(data);
      
      if (data.phase !== "idle" && data.phase !== "error") {
        setIsSyncing(true);
        if (data.message) {
          addLog(data.message);
        }
      } else {
        if (isSyncing) {
          setIsSyncing(false);
          fetchStats(); // Refresh stats when done
        }
      }
      
      if (data.phase === "error") {
        setError(data.message);
      }
    } catch (err) {
      console.error("Failed to fetch sync status");
    }
  }

  async function startSync() {
    setError(null);
    setLogs([]);
    addLog("[SYSTEM] Initializing metadata vectorization sequence...");
    addLog("[CORE] Preparing deep recursive traversal (Movies, Episodes, Albums)...");
    
    try {
      const res = await fetch(`${API_BASE}/api/rag/sync`, { method: "POST" });
      const data = await res.json();
      if (data.success) {
        setIsSyncing(true);
      } else {
        setError(data.error || "Failed to start sync");
        addLog(`[ERROR] ${data.error}`);
      }
    } catch (err) {
      setError("Connection error");
    }
  }

  function addLog(msg: string) {
    setLogs(prev => {
      // Avoid identical consecutive logs
      if (prev.length > 0 && prev[prev.length - 1].includes(msg)) return prev;
      const timestamp = new Date().toLocaleTimeString();
      return [...prev.slice(-100), `[${timestamp}] ${msg}`];
    });
  }

  return (
    <div className="flex flex-col gap-6 w-full animate-in fade-in slide-in-from-bottom-4 duration-700">
      {/* Top Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          label="Vector Count" 
          value={stats?.count?.toLocaleString() || "0"} 
          subValue="Total Documents"
          icon={Database}
          color="amber"
        />
        <StatCard 
          label="Neural Engine" 
          value={stats?.backend === "lancedb" ? "LanceDB" : "Shared"} 
          subValue="all-MiniLM-L6-v2"
          icon={Brain}
          color="blue"
        />
        <StatCard 
          label="Traversal Mode" 
          value="Recursive" 
          subValue="Deep Metadata"
          icon={Zap}
          color="purple"
        />
        <StatCard 
          label="System Status" 
          value={isSyncing ? "SYNCING" : "IDLE"} 
          subValue={isSyncing ? "Indexing sub-items..." : "Standby"}
          icon={Activity}
          color={isSyncing ? "amber" : "emerald"}
          active={isSyncing}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Controls & Info */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="glass-panel p-6 flex flex-col gap-6">
            <div className="flex items-center gap-2">
              <RefreshCcw className={`w-5 h-5 text-amber ${isSyncing ? "animate-spin" : ""}`} />
              <h3 className="text-lg font-bold text-white uppercase tracking-wider">Sync Control</h3>
            </div>
            
            <p className="text-sm text-slate-400 group relative">
              Synchronize your Plex metadata with the vector store. This process recursively indexes Movies, Shows (Episodes), and Music (Albums) with parent context enrichment.
              <span className="block mt-2 text-amber/80 text-xs italic">SOTA Industrial Standard v13.1 Compliance</span>
            </p>

            <button
              onClick={startSync}
              disabled={isSyncing}
              className={`w-full py-4 rounded-lg font-bold flex items-center justify-center gap-2 transition-all ${
                isSyncing 
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700" 
                : "bg-amber text-slate-900 hover:bg-amber/90 active:scale-[0.98] shadow-lg shadow-amber/20"
              }`}
            >
              {isSyncing ? <Activity className="w-5 h-5 animate-pulse" /> : <RefreshCcw className="w-5 h-5" />}
              {isSyncing ? "INGESTION IN PROGRESS" : "START DEEP INDEXING"}
            </button>

            <div className="pt-4 border-t border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Searchable Entities</span>
                <span className="text-slate-300">Movies, Episodes, Albums</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Context Enrichment</span>
                <span className="text-emerald-500">Wikipedia (Active)</span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-500">Local Cache</span>
                <span className="text-blue-400">LanceDB Enabled</span>
              </div>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-lg bg-red-900/20 border border-red-500/50 flex gap-3 text-red-200 animate-in shake duration-500">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <div className="flex flex-col gap-1">
                <span className="text-sm font-bold uppercase">System Error</span>
                <span className="text-xs opacity-80">{error}</span>
              </div>
            </div>
          )}
        </div>

        {/* Telemetry Log */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <div className="glass-panel-strong flex-1 flex flex-col min-h-[500px] border-l-4 border-amber/30">
            <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/30">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-amber" />
                <span className="text-xs font-bold text-slate-300 uppercase tracking-widest">Ingestion Telemetry</span>
              </div>
              {isSyncing && (
                <div className="flex items-center gap-4">
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-500 uppercase">Progress</span>
                    <span className="text-xs font-mono text-amber">
                      LIB {syncStatus?.library_index || 0}/{syncStatus?.libraries_total || 0}
                    </span>
                  </div>
                  <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-amber transition-all duration-500"
                      style={{ width: `${((syncStatus?.library_index || 0) / (syncStatus?.libraries_total || 1)) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
            
            <div className="flex-1 p-4 font-mono text-[11px] overflow-y-auto bg-black/40 space-y-1">
              {logs.length === 0 && !isSyncing && (
                <div className="h-full flex flex-col items-center justify-center text-slate-700 opacity-50">
                  <Terminal className="w-12 h-12 mb-2" />
                  <span>Telemetry feed idle. Initialize sync to begin...</span>
                </div>
              )}
              {logs.map((log, i) => (
                <div key={i} className={`flex gap-3 leading-relaxed ${
                  log.includes("[ERROR]") ? "text-red-400" : 
                  log.includes("[SUCCESS]") ? "text-emerald-400" : 
                  log.includes("[SYSTEM]") ? "text-amber font-bold" : 
                  "text-slate-400"
                }`}>
                  <span className="opacity-40 shrink-0">{log.substring(0, 11)}</span>
                  <span>{log.substring(12)}</span>
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, subValue, icon: Icon, color, active }: any) {
  const colorMap: any = {
    amber: "text-amber bg-amber/10 border-amber/20",
    blue: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    purple: "text-purple-400 bg-purple-400/10 border-purple-400/20",
    emerald: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
  };

  return (
    <div className={`glass-panel p-4 border-b-2 transition-all duration-500 ${active ? "border-amber translate-y-[-2px]" : "border-transparent"}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{label}</span>
        <div className={`p-1.5 rounded-md ${colorMap[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="flex flex-col">
        <span className="text-2xl font-bold text-white tabular-nums">{value}</span>
        <span className="text-[10px] text-slate-500">{subValue}</span>
      </div>
    </div>
  );
}
