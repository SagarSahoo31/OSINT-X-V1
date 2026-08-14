"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { Clock, ArrowLeft, ShieldAlert, Sparkles, CheckCircle2 } from "lucide-react";
import { getInvestigationTimeline } from "@/lib/api";
import { TimelineEvent } from "@/types";

export default function InvestigationTimelinePage() {
  const params = useParams();
  const id = params.id as string;

  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInvestigationTimeline(id)
      .then((data) => {
        setEvents(data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

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
            <Clock className="w-4 h-4 text-primary" />
            <span>Discovery & Intelligence Timeline</span>
          </h1>
          <p className="text-xs text-slate-400">
            Chronological progression of discoveries, asset identifications, and risk evaluations.
          </p>
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="p-6 rounded-xl bg-surface border border-border">
        {loading ? (
          <div className="py-12 text-center text-slate-500 text-sm">Loading discovery timeline...</div>
        ) : events.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-sm">No timeline events recorded yet.</div>
        ) : (
          <div className="relative pl-6 border-l border-border/80 space-y-6">
            {events.map((event, idx) => {
              const isCrit = event.severity === "CRITICAL" || event.severity === "HIGH";

              return (
                <div key={idx} className="relative group">
                  <div
                    className={`absolute -left-[31px] top-0.5 w-4 h-4 rounded-full border-2 bg-surface ${
                      isCrit
                        ? "border-risk-critical text-risk-critical"
                        : "border-primary text-primary"
                    }`}
                  />
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-[11px] text-slate-500">
                        {new Date(event.timestamp).toLocaleString()}
                      </span>
                      {event.source && (
                        <span className="px-1.5 py-0.2 rounded bg-slate-800 border border-slate-700 text-[10px] font-mono text-slate-300">
                          {event.source}
                        </span>
                      )}
                    </div>
                    <div className="text-sm font-semibold text-white">{event.title}</div>
                    <div className="text-xs text-slate-400 leading-relaxed">{event.description}</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
