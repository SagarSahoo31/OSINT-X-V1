"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Plus,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  Filter,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import { createInvestigation, listInvestigations, validateTarget } from "@/lib/api";
import { InvestigationSummary, TargetType } from "@/types";

export default function InvestigationsPage() {
  const [investigations, setInvestigations] = useState<InvestigationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [showWizard, setShowWizard] = useState(false);

  // Wizard state
  const [title, setTitle] = useState("");
  const [targetInput, setTargetInput] = useState("");
  const [targetType, setTargetType] = useState<TargetType>("DOMAIN");
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [authNotes, setAuthNotes] = useState("");
  const [validationResult, setValidationResult] = useState<any>(null);
  const [creating, setCreating] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const refreshList = () => {
    setLoading(true);
    listInvestigations()
      .then((data) => {
        setInvestigations(data.items || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    refreshList();
  }, []);

  const handleValidateTarget = async () => {
    if (!targetInput) return;
    setErrorMsg("");
    try {
      const res = await validateTarget(targetInput, targetType);
      setValidationResult(res);
      if (!res.is_valid) {
        setErrorMsg(res.error_message || "Invalid target format");
      }
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleLaunchScan = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    if (!isAuthorized) {
      setErrorMsg("Target authorization confirmation is required.");
      return;
    }

    setCreating(true);
    try {
      const inv = await createInvestigation({
        title: title || `${targetType} Scan: ${targetInput}`,
        target_input: targetInput,
        target_type: targetType,
        is_authorized: isAuthorized,
        authorization_notes: authNotes,
      });
      setShowWizard(false);
      setTitle("");
      setTargetInput("");
      setValidationResult(null);
      setCreating(false);
      refreshList();
    } catch (err: any) {
      setErrorMsg(err.message);
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Investigations Hub</h1>
          <p className="text-sm text-slate-400 mt-1">
            Create, manage, and monitor defensive intelligence collection missions.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={refreshList}
            className="p-2 rounded-lg bg-surface border border-border hover:bg-surfaceHover text-slate-300 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            onClick={() => setShowWizard(true)}
            className="px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-semibold transition flex items-center gap-2 glow-blue"
          >
            <Plus className="w-4 h-4" />
            <span>Launch Investigation</span>
          </button>
        </div>
      </div>

      {/* Launch Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-border w-full max-w-xl rounded-xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Search className="w-5 h-5 text-primary" />
                <span>Launch New Defensive Investigation</span>
              </h2>
              <button
                onClick={() => setShowWizard(false)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleLaunchScan} className="space-y-4 text-xs">
              {errorMsg && (
                <div className="p-3 rounded-lg bg-risk-critical/10 border border-risk-critical/30 text-risk-critical flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <div>
                <label className="block text-slate-300 font-medium mb-1">Target Type</label>
                <div className="grid grid-cols-5 gap-2">
                  {(["DOMAIN", "EMAIL", "USERNAME", "IP", "URL"] as TargetType[]).map((t) => (
                    <button
                      type="button"
                      key={t}
                      onClick={() => {
                        setTargetType(t);
                        setValidationResult(null);
                      }}
                      className={`py-2 rounded-lg font-mono font-medium transition ${
                        targetType === t
                          ? "bg-primary text-white border border-primary-light"
                          : "bg-background border border-border text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Target Value</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    required
                    placeholder={
                      targetType === "DOMAIN"
                        ? "e.g., example.com"
                        : targetType === "EMAIL"
                        ? "e.g., analyst@example.com"
                        : targetType === "USERNAME"
                        ? "e.g., security_lead"
                        : targetType === "IP"
                        ? "e.g., 198.51.100.25"
                        : "https://example.com"
                    }
                    value={targetInput}
                    onChange={(e) => {
                      setTargetInput(e.target.value);
                      setValidationResult(null);
                    }}
                    onBlur={handleValidateTarget}
                    className="flex-1 px-3 py-2 rounded-lg bg-background border border-border text-slate-100 placeholder-slate-600 focus:outline-none focus:border-primary font-mono"
                  />
                  <button
                    type="button"
                    onClick={handleValidateTarget}
                    className="px-3 py-2 rounded-lg bg-surfaceHover border border-border hover:bg-slate-700 text-slate-200"
                  >
                    Validate
                  </button>
                </div>
                {validationResult?.is_valid && (
                  <div className="mt-1.5 flex items-center gap-1.5 text-emerald-400 text-[11px] font-mono">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Canonical Target: {validationResult.canonical_target}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Investigation Title</label>
                <input
                  type="text"
                  placeholder="Optional title (auto-generated if empty)"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-slate-100 placeholder-slate-600 focus:outline-none focus:border-primary"
                />
              </div>

              <div className="p-3.5 rounded-lg bg-background border border-border space-y-2">
                <div className="flex items-start gap-2.5">
                  <input
                    type="checkbox"
                    id="auth_check"
                    checked={isAuthorized}
                    onChange={(e) => setIsAuthorized(e.target.checked)}
                    className="mt-0.5 rounded border-slate-700 bg-slate-900 text-primary focus:ring-0"
                  />
                  <label htmlFor="auth_check" className="text-slate-200 font-medium cursor-pointer">
                    I confirm this target is authorized for defensive security assessment.
                  </label>
                </div>
                <p className="text-[11px] text-slate-500 pl-6">
                  OSINT-X enforces defensive compliance. Scans against unauthorized targets are strictly prohibited.
                </p>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Authorization Notes (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g., CTF Lab / Customer Contract Ref #1042"
                  value={authNotes}
                  onChange={(e) => setAuthNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-background border border-border text-slate-100 placeholder-slate-600 focus:outline-none focus:border-primary"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowWizard(false)}
                  className="px-4 py-2 rounded-lg bg-surfaceHover hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-5 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white font-medium glow-blue disabled:opacity-50"
                >
                  {creating ? "Launching..." : "Launch Investigation"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Investigation List */}
      <div className="p-5 rounded-xl bg-surface border border-border">
        {loading ? (
          <div className="py-12 text-center text-sm text-slate-500">Loading investigations...</div>
        ) : investigations.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">No investigations found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-border text-slate-400 uppercase font-mono">
                <tr>
                  <th className="py-2.5 px-3">Title & Target</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">Assets</th>
                  <th className="py-2.5 px-3">Findings</th>
                  <th className="py-2.5 px-3">OSINT-X Risk</th>
                  <th className="py-2.5 px-3">Created</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-slate-300">
                {investigations.map((inv) => {
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
                        <Link
                          href={`/investigations/${inv.id}`}
                          className="font-medium text-white hover:text-primary-light transition"
                        >
                          {inv.title}
                        </Link>
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
                      <td className="py-3 px-3 font-mono">{inv.entities_count}</td>
                      <td className="py-3 px-3 font-mono">{inv.findings_count}</td>
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
                          className="inline-flex items-center gap-1 px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 transition"
                        >
                          <span>Open</span>
                          <ExternalLink className="w-3 h-3" />
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
