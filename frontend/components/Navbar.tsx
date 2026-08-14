"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Shield, Activity, Bell, Terminal } from "lucide-react";
import { fetchHealth } from "@/lib/api";

export function Navbar() {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(() => setHealthy(true))
      .catch(() => setHealthy(false));
  }, []);

  return (
    <header className="h-16 border-b border-border bg-surface/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-40">
      <div className="flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-primary/20 border border-primary flex items-center justify-center text-primary glow-blue">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-bold text-lg tracking-wider text-white">
            OSINT<span className="text-primary">-X</span>
          </span>
        </Link>
        <span className="text-xs px-2 py-0.5 rounded bg-primary/10 text-primary border border-primary/30 font-mono">
          DEFENSIVE SOC
        </span>
      </div>

      <div className="flex items-center gap-4 text-sm">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-background border border-border">
          <span
            className={`w-2 h-2 rounded-full ${
              healthy === true
                ? "bg-risk-low shadow-[0_0_8px_#16a34a]"
                : healthy === false
                ? "bg-risk-critical shadow-[0_0_8px_#dc2626]"
                : "bg-yellow-500 animate-pulse"
            }`}
          />
          <span className="text-xs text-slate-300 font-mono">
            {healthy === true ? "API ONLINE" : healthy === false ? "API OFFLINE" : "CHECKING"}
          </span>
        </div>

        <Link
          href="/investigations"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-primary hover:bg-primary-hover text-white text-xs font-medium transition"
        >
          <Terminal className="w-3.5 h-3.5" />
          <span>Launch Scan</span>
        </Link>
      </div>
    </header>
  );
}
