"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Search,
  Globe,
  Users,
  Activity,
  AlertTriangle,
  ArrowUpRight,
  TrendingUp,
} from "lucide-react";
import { listInvestigations } from "@/lib/api";
import { InvestigationSummary } from "@/types";

export default function DashboardPage() {
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listInvestigations()
      .then((data) => {
        setInvestigations(data.items || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const totalInvestigations = investigations.length;
  const completedCount = investigations.filter((i) => i.status === "COMPLETED").length;
  const highRiskCount = investigations.filter((i) => (i.risk_score || 0) >= 70).length;
  const totalAssets = investigations.reduce((acc, curr) => acc + (curr.entities_count || 0), 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            Security Intelligence & Attack-Surface Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time defensive exposure monitoring across authorized assets and identities.
          </p>
        </div>
        <Link
          href="/investigations"
          className="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-semibold transition flex items-center gap-2 glow-blue"
        >
          <Search className="w-4 h-4" />
          <span>New Investigation</span>
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-surface border border-border">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Total Scans</span>
            <Activity className="w-4 h-4 text-primary" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">{totalInvestigations}</div>
          <div className="text-xs text-slate-500 mt-1">{completedCount} completed scans</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Correlated Assets</span>
            <Globe className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">{totalAssets}</div>
          <div className="text-xs text-slate-500 mt-1">Canonical graph entities</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">High Exposure Targets</span>
            <ShieldAlert className="w-4 h-4 text-risk-critical" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">{highRiskCount}</div>
          <div className="text-xs text-slate-500 mt-1">Risk Score &ge; 70/100</div>
        </div>

        <div className="p-4 rounded-xl bg-surface border border-border">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium uppercase tracking-wider">Defense State</span>
            <TrendingUp className="w-4 h-4 text-primary-light" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">ACTIVE</div>
          <div className="text-xs text-slate-500 mt-1">Passive & Probing Sandbox</div>
        </div>
      </div>

      {/* Recent Investigations Table */}
      <div className="p-5 rounded-xl bg-surface border border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-white">Recent Investigations</h2>
          <Link
            href="/investigations"
            className="text-xs text-primary hover:text-primary-light flex items-center gap-1 transition"
          >
            <span>View All</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="py-12 text-center text-sm text-slate-500">Loading investigations...</div>
        ) : investigations.length === 0 ? (
          <div className="py-12 text-center space-y-3">
            <Search className="w-8 h-8 text-slate-600 mx-auto" />
            <div className="text-sm text-slate-400">No investigations recorded yet.</div>
            <Link
              href="/investigations"
              className="inline-block px-3 py-1.5 rounded bg-primary text-xs text-white"
            >
              Start your first investigation
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border text-slate-400 uppercase font-mono">
                <tr>
                  <th className="py-2.5 px-3">Title & Target</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Discovered Assets</th>
                  <th className="py-2.5 px-3">OSINT-X Risk Score</th>
                  <th className="py-2.5 px-3">Created</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-slate-300">
                {investigations.slice(0, 8).map((inv) => {
                  const riskVal = inv.risk_score || 0;
                  const riskColor =
                    riskVal >= 75
                      ? "text-risk-critical bg-risk-critical/10 border-risk-critical/30"
                      : riskVal >= 40
                      ? "text-risk-high bg-risk-high/10 border-risk-high/30"
                      : "text-risk-low bg-risk-low/10 border-risk-low/30";

                  return (
                    <tr key={inv.id} className="hover:bg-surfaceHover/50 transition">
                      <td className="py-3 px-3">
                        <div className="font-medium text-white">{inv.title}</div>
                        <div className="text-slate-500 font-mono text-[11px]">{inv.target_input}</div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-300">
                          {inv.target_type}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary-light text-[10px] font-mono">
                          {inv.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono">{inv.entities_count} assets</td>
                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded border text-[11px] font-bold font-mono ${riskColor}`}>
                          {inv.risk_score !== null ? `${inv.risk_score}/100` : "Pending"}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-slate-500 font-mono">
                        {new Date(inv.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-3 text-right">
                        <Link
                          href={`/investigations/${inv.id}`}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
                        >
                          Overview
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
