"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Search,
  Network,
  Activity,
  FileText,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Investigations", href: "/investigations", icon: Search },
  { label: "Monitoring & Drift", href: "/monitoring", icon: Activity },
  { label: "Settings & System", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-surface flex flex-col justify-between p-4 shrink-0 min-h-[calc(100vh-4rem)]">
      <nav className="space-y-1.5">
        <div className="text-[10px] font-mono text-slate-500 uppercase tracking-widest px-3 mb-3">
          Core Operations
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition ${
                isActive
                  ? "bg-primary/15 text-primary-light border border-primary/30"
                  : "text-slate-400 hover:text-slate-100 hover:bg-surfaceHover"
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-3 rounded-lg bg-background border border-border text-xs text-slate-400">
        <div className="text-slate-200 font-medium mb-1">Defensive Mode Active</div>
        <div className="text-[11px] text-slate-500">
          Authorization constraints & passive sandbox enabled.
        </div>
      </div>
    </aside>
  );
}
