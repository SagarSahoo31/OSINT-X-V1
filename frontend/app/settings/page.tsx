"use client";

import React, { useEffect, useState } from "react";
import { Settings, Shield, Server, Cpu, Database, CheckCircle2, XCircle } from "lucide-react";
import { fetchHealth } from "@/lib/api";

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const collectors = [
    { name: "OWASP Amass", role: "Domain & ASN Attack-Surface Recon", type: "Active / Passive", status: "Enabled" },
    { name: "DNS Resolver", role: "A, AAAA, MX, TXT, CNAME Resolution", type: "Passive / Direct", status: "Enabled" },
    { name: "HTTPX Prober", role: "Port & TLS & Header Fingerprinting", type: "Passive / Probing", status: "Enabled" },
    { name: "WhatWeb", role: "Technology Stack Identification", type: "Header / Body Analysis", status: "Enabled" },
    { name: "crt.sh", role: "Certificate Transparency Logs", type: "Passive API", status: "Enabled" },
    { name: "Holehe", role: "Email Registered Service Discovery", type: "Defensive OSINT", status: "Enabled" },
    { name: "Maigret", role: "Username Account Presence Discovery", type: "Defensive OSINT", status: "Enabled" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">System Settings & Architecture</h1>
        <p className="text-sm text-slate-400 mt-1">
          Diagnostics, collector pipeline configurations, and defensive guardrail statuses.
        </p>
      </div>

      {/* Defensive Guardrails Summary */}
      <div className="p-5 rounded-xl bg-surface border border-border space-y-3">
        <div className="flex items-center gap-2 text-primary">
          <Shield className="w-5 h-5" />
          <h2 className="text-sm font-bold text-white uppercase tracking-wider">
            Defensive Scope & Ethical Boundary Guardrails
          </h2>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          OSINT-X enforces defensive compliance. The platform prohibits exploit payloads, credential stuffing, or unauthorized invasive actions.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2 text-xs">
          <div className="p-3 rounded bg-background border border-border">
            <span className="text-[10px] text-slate-500 font-mono uppercase">Private IP Scans</span>
            <div className="font-bold text-rose-400 font-mono mt-0.5">BLOCKED (RFC 1918 Safe)</div>
          </div>
          <div className="p-3 rounded bg-background border border-border">
            <span className="text-[10px] text-slate-500 font-mono uppercase">Target Authorization</span>
            <div className="font-bold text-emerald-400 font-mono mt-0.5">MANDATORY CHECK</div>
          </div>
          <div className="p-3 rounded bg-background border border-border">
            <span className="text-[10px] text-slate-500 font-mono uppercase">Subprocess Execution</span>
            <div className="font-bold text-primary-light font-mono mt-0.5">SANDBOXED (shell=False)</div>
          </div>
        </div>
      </div>

      {/* Infrastructure Components */}
      <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
        <h2 className="text-base font-semibold text-white flex items-center gap-2">
          <Server className="w-4 h-4 text-primary" />
          <span>Core Infrastructure Diagnostics</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
          <div className="p-3.5 rounded-lg bg-background border border-border space-y-1">
            <div className="flex items-center justify-between text-slate-400 font-mono text-[10px]">
              <span>POSTGRESQL 16</span>
              <Database className="w-3.5 h-3.5 text-primary" />
            </div>
            <div className="font-bold text-slate-200">Authoritative Relational DB</div>
            <div className="text-[10px] text-emerald-400">ONLINE (SQLAlchemy 2.0)</div>
          </div>

          <div className="p-3.5 rounded-lg bg-background border border-border space-y-1">
            <div className="flex items-center justify-between text-slate-400 font-mono text-[10px]">
              <span>REDIS 7</span>
              <Server className="w-3.5 h-3.5 text-rose-400" />
            </div>
            <div className="font-bold text-slate-200">Celery Message Broker</div>
            <div className="text-[10px] text-emerald-400">READY (Task Queue)</div>
          </div>

          <div className="p-3.5 rounded-lg bg-background border border-border space-y-1">
            <div className="flex items-center justify-between text-slate-400 font-mono text-[10px]">
              <span>NEO4J 5</span>
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="font-bold text-slate-200">Intelligence Graph DB</div>
            <div className="text-[10px] text-primary-light">SYNC SERVICE READY</div>
          </div>

          <div className="p-3.5 rounded-lg bg-background border border-border space-y-1">
            <div className="flex items-center justify-between text-slate-400 font-mono text-[10px]">
              <span>LOCAL OLLAMA</span>
              <Cpu className="w-3.5 h-3.5 text-purple-400" />
            </div>
            <div className="font-bold text-slate-200">Local LLM AI Analyst</div>
            <div className="text-[10px] text-purple-400">HYBRID / FALLBACK ACTIVE</div>
          </div>
        </div>
      </div>

      {/* Collector Catalog Table */}
      <div className="p-5 rounded-xl bg-surface border border-border space-y-4">
        <h2 className="text-base font-semibold text-white">Registered Collector Adapters</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-border text-slate-400 uppercase font-mono">
              <tr>
                <th className="py-2.5 px-3">Collector Name</th>
                <th className="py-2.5 px-3">Intelligence Domain</th>
                <th className="py-2.5 px-3">Execution Mode</th>
                <th className="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 text-slate-300 font-mono">
              {collectors.map((c, i) => (
                <tr key={i} className="hover:bg-surfaceHover/50 transition">
                  <td className="py-3 px-3 font-bold text-white">{c.name}</td>
                  <td className="py-3 px-3 text-slate-400">{c.role}</td>
                  <td className="py-3 px-3 text-slate-400">{c.type}</td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[10px]">
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
