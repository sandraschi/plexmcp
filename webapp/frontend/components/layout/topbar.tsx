"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Film, HelpCircle, FileText, ChevronDown, ExternalLink } from "lucide-react";
import { HelpModal } from "./help-modal";
import { LoggerModal } from "./logger-modal";

const WEBAPP_ZOO: { label: string; url: string; port?: number }[] = [
  { label: "PlexMCP", url: "http://127.0.0.1:10741", port: 10741 },
  { label: "Advanced Memory", url: "http://127.0.0.1:10704", port: 10704 },
  { label: "Calibre MCP", url: "http://127.0.0.1:10721", port: 10721 },
  { label: "Robotics MCP", url: "http://127.0.0.1:10706", port: 10706 },
  { label: "MyAI Dashboard", url: "http://127.0.0.1:3060", port: 3060 },
  { label: "Virtualization MCP", url: "http://127.0.0.1:10700", port: 10700 },
  { label: "Database Ops MCP", url: "http://127.0.0.1:10708", port: 10708 },
  { label: "Avatar MCP", url: "http://127.0.0.1:10710", port: 10710 },
  { label: "VRChat MCP", url: "http://127.0.0.1:10712", port: 10712 },
  { label: "Ring MCP", url: "http://127.0.0.1:10728", port: 10728 },
  { label: "MyAI Calibre Plus", url: "http://127.0.0.1:10734", port: 10734 },
  { label: "MyAI Plex Plus", url: "http://127.0.0.1:10760", port: 10760 },
  { label: "Games App", url: "http://127.0.0.1:10726", port: 10726 },
];

export function Topbar() {
  const [showHelp, setShowHelp] = useState(false);
  const [showLogger, setShowLogger] = useState(false);
  const [showZoo, setShowZoo] = useState(false);
  const zooRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!showZoo) return;
    const close = (e: MouseEvent) => {
      if (zooRef.current && !zooRef.current.contains(e.target as Node)) setShowZoo(false);
    };
    document.addEventListener("click", close);
    return () => document.removeEventListener("click", close);
  }, [showZoo]);

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-slate-700/50 glass-panel-strong">
        <div className="container mx-auto px-4 h-14 flex items-center justify-between gap-4">
          <Link href="/" className="text-xl font-semibold text-amber shrink-0 flex items-center gap-2">
            <Film className="w-6 h-6" />
            PlexMCP
          </Link>
          <div className="flex items-center gap-2">
            <div className="relative" ref={zooRef}>
              <button
                type="button"
                onClick={() => setShowZoo(!showZoo)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-md text-slate-300 hover:bg-slate-700/50 hover:text-amber text-sm"
                title="Jump to other webapps"
              >
                <ExternalLink className="w-4 h-4" />
                <span className="hidden sm:inline">Webapps</span>
                <ChevronDown className={`w-4 h-4 transition-transform ${showZoo ? "rotate-180" : ""}`} />
              </button>
              {showZoo && (
                <div className="absolute right-0 mt-1 py-1 w-56 max-h-80 overflow-auto rounded-lg glass-panel border border-slate-600/50 shadow-xl z-50">
                  {WEBAPP_ZOO.map((app) => (
                    <a
                      key={app.url}
                      href={app.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block px-4 py-2 text-sm text-slate-200 hover:bg-slate-700/80 hover:text-amber"
                    >
                      {app.label}
                      {app.port != null && <span className="text-slate-500 text-xs ml-1">:{app.port}</span>}
                    </a>
                  ))}
                </div>
              )}
            </div>
            <button
              type="button"
              onClick={() => setShowHelp(true)}
              className="p-2 rounded-md text-slate-400 hover:bg-slate-700/50 hover:text-amber"
              title="Help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={() => setShowLogger(true)}
              className="p-2 rounded-md text-slate-400 hover:bg-slate-700/50 hover:text-amber"
              title="Logs"
            >
              <FileText className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>
      {showHelp && <HelpModal onClose={() => setShowHelp(false)} />}
      {showLogger && <LoggerModal onClose={() => setShowLogger(false)} />}
    </>
  );
}
