"use client";

import { Hammer, Wrench } from "lucide-react";
import { RepairDashboard } from "@/components/repair/repair-dashboard";

export default function RepairPage() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <header className="flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber/20">
            <Wrench className="w-6 h-6 text-amber" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Media Repair Hub</h1>
        </div>
        <p className="text-slate-400 max-w-2xl px-1">
          Technical maintenance and industrial-grade media repairs. Sync audio/subtitles, 
          fix aspect ratios, and extract hidden streams with surgical precision.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6">
        <RepairDashboard />
      </div>
    </div>
  );
}
