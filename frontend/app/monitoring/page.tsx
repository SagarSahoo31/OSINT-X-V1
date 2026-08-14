"use client";

import React, { useEffect, useState } from "react";
import { Activity, ArrowRight, TrendingUp, TrendingDown, Minus, RefreshCw } from "lucide-react";
import { compareScans, listInvestigations } from "@/lib/api";
import { InvestigationSummary, ScanComparison } from "@/types";

export default function MonitoringPage() {
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [baselineId, setBaselineId] = useState("");
  const [currentId, setCurrentId] = useState("");
  const [comparison, setComparison] = useState<ScanComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    listInvestigations().then((data) => {
      const items = data.items || [];
      setInvestigations(items);
      if (items.length >= 2) {
        setBaselineId(items[1].id);
        setCurrentId(items[0].id);
      } else if (items.length === 1) {
        setBaselineId(items[0].id);
        setCurrentId(items[0].id);
      }
    });
  }, []);

  const handleCompare = async () => {
    if (!baselineId || !currentId) return;
    setLoading(true);
    setErrorMsg("");
    try {
      const res = await compareScans(baselineId, currentId);
      setComparison(res);
      setLoading(false);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to compare scans");
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Continuous Monitoring & Drift</h1>
          <p className="text-sm text-slate-400 mt-1">
            Compare sequential scans against target assets to detect new attack-surface exposures.
          </p>
        </div>
      </div>

      {/* Selector Bar */}
      <div className="p-5 rounded-xl bg-surface border border-border space-y-4 text-xs">
        <h2 className="font-semibold text-white">Select Scans to Compare</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-slate-400 mb-1">Baseline Scan (Earlier)</label>
            <select
              value={baselineId}
              onChange={(e) => setBaselineId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-slate-200 font-mono focus:outline-none"
            >
              {investigations.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.title} ({new Date(i.created_at).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-400 mb-1">Current Scan (Latest)</label>
            <select
              value={currentId}
              onChange={(e) => setCurrentId(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-slate-200 font-mono focus:outline-none"
            >
              {investigations.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.title} ({new Date(i.created_at).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleCompare}
            disabled={loading || !baselineId || !currentId}
            className="w-full py-2 rounded-lg bg-primary hover:bg-primary-hover text-white font-semibold transition disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            <span>Run Delta Analysis</span>
          </button>
        </div>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="space-y-6">
          {/* Top KPI row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-surface border border-border">
              <span className="text-slate-400 uppercase font-mono text-[10px]">Risk Score Change</span>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-2xl font-bold text-white">
                  {comparison.risk_assessment.current_score}/100
                </span>
                <span
                  className={`text-xs font-mono font-bold flex items-center gap-0.5 ${
                    comparison.risk_assessment.risk_delta > 0
                      ? "text-risk-critical"
                      : comparison.risk_assessment.risk_delta < 0
                      ? "text-risk-low"
                      : "text-slate-400"
                  }`}
                >
                  {comparison.risk_assessment.risk_delta > 0 ? "+" : ""}
                  {comparison.risk_assessment.risk_delta} pts
                </span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-surface border border-border">
              <span className="text-slate-400 uppercase font-mono text-[10px]">New Discovered Assets</span>
              <div className="text-2xl font-bold text-emerald-400 mt-2 font-mono">
                +{comparison.asset_changes.new_assets_count}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-surface border border-border">
              <span className="text-slate-400 uppercase font-mono text-[10px]">Removed Assets</span>
              <div className="text-2xl font-bold text-rose-400 mt-2 font-mono">
                -{comparison.asset_changes.removed_assets_count}
              </div>
            </div>
          </div>

          {/* Asset Deltas List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {/* Added */}
            <div className="p-5 rounded-xl bg-surface border border-border space-y-3">
              <h3 className="font-semibold text-emerald-400 flex items-center gap-1.5">
                <span>Newly Detected Assets</span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 text-[10px] font-mono">
                  {comparison.asset_changes.new_assets.length}
                </span>
              </h3>
              {comparison.asset_changes.new_assets.length === 0 ? (
                <div className="text-slate-500 py-6 text-center">No new assets detected in this scan.</div>
              ) : (
                <div className="space-y-1.5 max-h-64 overflow-y-auto">
                  {comparison.asset_changes.new_assets.map((a, i) => (
                    <div
                      key={i}
                      className="p-2 rounded bg-background border border-border flex items-center justify-between font-mono"
                    >
                      <span className="text-slate-200">{a.display}</span>
                      <span className="text-[10px] text-emerald-400">{a.type}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Removed */}
            <div className="p-5 rounded-xl bg-surface border border-border space-y-3">
              <h3 className="font-semibold text-rose-400 flex items-center gap-1.5">
                <span>Removed / Decommissioned Assets</span>
                <span className="px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 text-[10px] font-mono">
                  {comparison.asset_changes.removed_assets.length}
                </span>
              </h3>
              {comparison.asset_changes.removed_assets.length === 0 ? (
                <div className="text-slate-500 py-6 text-center">No assets decommissioned.</div>
              ) : (
                <div className="space-y-1.5 max-h-64 overflow-y-auto">
                  {comparison.asset_changes.removed_assets.map((a, i) => (
                    <div
                      key={i}
                      className="p-2 rounded bg-background border border-border flex items-center justify-between font-mono"
                    >
                      <span className="text-slate-400 line-through">{a.display}</span>
                      <span className="text-[10px] text-rose-400">{a.type}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
