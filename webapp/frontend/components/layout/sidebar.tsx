"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Library, Search, Server, MessageSquare, Film, Settings, ChevronLeft, ChevronRight } from "lucide-react";

const navItems = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/libraries", label: "Libraries", icon: Library },
  { href: "/movies", label: "Movies", icon: Film },
  { href: "/search", label: "Search", icon: Search },
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/server", label: "Server", icon: Server },
  { href: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={`shrink-0 flex flex-col glass-panel-strong border-r border-slate-600/50 transition-[width] duration-200 ${collapsed ? "w-16 min-w-[4rem]" : "w-56 min-w-[14rem]"
        }`}
    >
      <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${isActive ? "bg-amber/20 text-amber" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                } ${collapsed ? "justify-center px-2" : ""}`}
              title={collapsed ? label : undefined}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>
      <button
        type="button"
        onClick={onToggle}
        className="flex items-center justify-center py-2 border-t border-slate-700 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
        title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
      </button>
    </aside>
  );
}
