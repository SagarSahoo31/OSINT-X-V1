"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  FileText,
  Download,
  ArrowLeft,
  FileCode,
  Table,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { generateReport } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function InvestigationReportsPage() {
  const params = useParams();
  const id = params.id as string;

  const [generating, setGenerating] = useState<string | null>(null);
  const [generatedReport, setGeneratedReport] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const handleGenerate = async (format: "PDF" | "JSON" | "CSV") => {
    setGenerating(format);
    setErrorMsg("");
    try {
      const report = await generateReport(id, format);
      setGeneratedReport(report);
      setGenerating(null);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to generate report");
      setGenerating(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-4 rounded-xl bg-surface border border-border flex items-center gap-3">
        <Link
          href={`/investigations/${id}`}
          className="p-1.5 rounded-lg bg-background border border-border hover:bg-surfaceHover text-slate-300 transition"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <div>
          <h1 className="text-base font-bold text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-primary" />
            <span>Deliverables & Assessment Reports</span>
          </h1>
          <p className="text-xs text-slate-400">
            Export structured findings, asset inventories, and executive risk documentation.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-risk-critical/10 border border-risk-critical/30 text-risk-critical text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Export Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* PDF Option */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <FileText className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Executive PDF Report</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Formatted document featuring executive risk scoring, scope, discovered assets, and defensive recommendations.
            </p>
          </div>
          <button
            onClick={() => handleGenerate("PDF")}
            disabled={generating === "PDF"}
            className="w-full py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold transition disabled:opacity-50"
          >
            {generating === "PDF" ? "Building PDF..." : "Generate PDF"}
          </button>
        </div>

        {/* JSON Option */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center text-primary-light">
              <FileCode className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Normalized JSON Export</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Full machine-readable deliverable containing entities, relationships, confidence, and provenance hashes.
            </p>
          </div>
          <button
            onClick={() => handleGenerate("JSON")}
            disabled={generating === "JSON"}
            className="w-full py-2 rounded-lg bg-surfaceHover hover:bg-slate-700 text-slate-200 text-xs font-semibold transition disabled:opacity-50"
          >
            {generating === "JSON" ? "Exporting JSON..." : "Generate JSON"}
          </button>
        </div>

        {/* CSV Option */}
        <div className="p-5 rounded-xl bg-surface border border-border space-y-4 flex flex-col justify-between">
          <div className="space-y-2">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Table className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white">Flattened Asset CSV</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Tabular spreadsheet of all normalized entity records, timestamps, confidence scores, and IDs.
            </p>
          </div>
          <button
            onClick={() => handleGenerate("CSV")}
            disabled={generating === "CSV"}
            className="w-full py-2 rounded-lg bg-surfaceHover hover:bg-slate-700 text-slate-200 text-xs font-semibold transition disabled:opacity-50"
          >
            {generating === "CSV" ? "Exporting CSV..." : "Generate CSV"}
          </button>
        </div>
      </div>

      {/* Generated Report Ready Banner */}
      {generatedReport && (
        <div className="p-5 rounded-xl bg-emerald-950/20 border border-emerald-800/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <div>
              <div className="text-sm font-bold text-white">{generatedReport.title} Ready</div>
              <div className="text-xs text-slate-400 font-mono">
                Format: {generatedReport.format} | Size: {(generatedReport.file_size_bytes / 1024).toFixed(1)} KB
              </div>
            </div>
          </div>
          <a
            href={`${API_BASE}/api/v1/reports/${generatedReport.id}/download`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Deliverable</span>
          </a>
        </div>
      )}
    </div>
  );
}
