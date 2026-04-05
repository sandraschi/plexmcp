"use client";

import { useState, useEffect } from "react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem("plex-sidebar-collapsed");
    if (stored !== null) setCollapsed(stored === "true");
  }, []);

  useEffect(() => {
    if (mounted) {
      localStorage.setItem("plex-sidebar-collapsed", String(collapsed));
    }
  }, [collapsed, mounted]);

  if (!mounted) {
    return <div className="min-h-screen bg-slate-900" />;
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Topbar />
      <div className="flex flex-1">
        <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
        <main className="flex-1 min-w-0">{children}</main>
      </div>
    </div>
  );
}
