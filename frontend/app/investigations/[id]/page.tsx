"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Shield,
  Network,
  Clock,
  FileText,
  Sparkles,
  RefreshCw,
  ExternalLink,
  AlertTriangle,
  Info,
  CheckCircle2,
  XCircle,
  Terminal,
} from "lucide-react";
import { getInvestigation, requestAIAnalysis } from "@/lib/api";
import { InvestigationDetail } from "@/types";

export default function InvestigationOverviewPage() {
  const params = useParams();
  const id = params.id as string;

  const [investigation, setInvestigation] = useState<InvestigationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);

  const fetchDetails = () => {
    getInvestigation(id)
      .then((data) => {
        setInvestigation(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleRunAI = async () => {
    setAiLoading(true);
    try {
      const res = await requestAIAnalysis(id);
      setAiAnalysis(res.analysis);
      setAiLoading(false);
    } catch (err) {
      setAiLoading(false);
    }
  };

  if (loading) {
    return <div className="py-16 text-center text-sm text-slate-500">Loading investigation details...</div>;
  }

  if (!investigation) {
    return (
      <div className="py-16 text-center text-slate-400">
        Investigation not found. <Link href="/investigations" className="text-primary underline">Return to list</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Sub-nav */}
      <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-bold text-white tracking-tight">{investigation.title}</h1>
              <span className="px-2 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary-light text-xs font-mono">
                {investigation.status}
              </span>
            </div>
            <div className="text-xs text-slate-400 font-mono mt-1">
              Target: <span className="text-slate-200">{investigation.target_input}</span> | Type:{" "}
              <span className="text-slate-200">{investigation.target_type}</span> | Created:{" "}
              <span className="text-slate-200">{new Date(investigation.created_at).toLocaleString()}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchDetails}
              className="p-2 rounded-lg bg-background border border-border hover:bg-surfaceHover text-slate-300 transition"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={handleRunAI}
              disabled={aiLoading}
              className="px-3.5 py-1.5 rounded-lg bg-purple-600/20 border border-purple-500/40 hover:bg-purple-600/30 text-purple-200 text-xs font-medium transition flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              <span>{aiLoading ? "Analyzing..." : "AI Analyst"}</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-t border-border pt-3 text-xs">
          <Link
            href={`/investigations/${id}`}
            className="px-3 py-1.5 rounded-lg bg-primary/20 text-primary-light border border-primary/30 font-medium"
          >
            Overview & Jobs
          </Link>
          <Link
            href={`/investigations/${id}/graph`}
            className="px-3 py-1.5 rounded-lg hover:bg-surfaceHover text-slate-400 hover:text-slate-200 transition font-medium flex items-center gap-1.5"
          >
            <Network className="w-3.5 h-3.5" />
            <span>Relationship Graph</span>
          </Link>
          <Link
            href={`/investigations/${id}/timeline`}
            className="px-3 py-1.5 rounded-lg hover:bg-surfaceHover text-slate-400 hover:text-slate-200 transition font-medium flex items-center gap-1.5"
          >
            <Clock className="w-3.5 h-3.5" />
            <span>Timeline</span>
          </Link>
          <Link
            href={`/investigations/${id}/reports`}
            className="px-3 py-1.5 rounded-lg hover:bg-surfaceHover text-slate-400 hover:text-slate-200 transition font-medium flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Reports & Exports</span>
          </Link>
        </div>
      </div>

      {/* AI Analyst Output Drawer */}
      {aiAnalysis && (
        <div className="p-5 rounded-xl bg-purple-950/20 border border-purple-900/50 space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-purple-300 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>OSINT-X AI Security Analyst Synthesis</span>
            </h3>
            <button
              onClick={() => setAiAnalysis(null)}
              className="text-xs text-purple-400 hover:text-purple-200"
            >
              Close
            </button>
          </div>
          <div className="text-xs text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
            {aiAnalysis}
          </div>
        </div>
      )}

      {/* Collector Jobs Status */}
      <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
        <h2 className="text-base font-semibold text-white">Collector Pipeline Execution</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {investigation.collector_jobs.map((job) => {
            const isDone = job.status === "COMPLETED";
            const isFailed = job.status === "FAILED" || job.status === "TIMED_OUT";

            return (
              <div
                key={job.id}
                className="p-3.5 rounded-lg bg-background border border-border space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-slate-200 uppercase">{job.collector_name}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono ${
                      isDone
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        : isFailed
                        ? "bg-rose-950 text-rose-300 border border-rose-800"
                        : "bg-primary/20 text-primary-light border border-primary/30"
                    }`}
                  >
                    {job.status}
                  </span>
                </div>
                <div className="text-slate-400 text-[11px]">
                  Discovered items: <span className="text-slate-200 font-mono">{job.items_count}</span>
                </div>
                {job.execution_duration_ms && (
                  <div className="text-slate-500 font-mono text-[10px]">
                    Runtime: {(job.execution_duration_ms / 1000).toFixed(2)}s
                  </div>
                )}
                {job.error_message && (
                  <div className="text-rose-400 text-[10px] line-clamp-1 font-mono">
                    {job.error_message}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
