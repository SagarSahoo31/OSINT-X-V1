"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  Network,
  Filter,
  Sliders,
  Maximize2,
  ZoomIn,
  ZoomOut,
  Info,
  ArrowLeft,
} from "lucide-react";
import { getInvestigationGraph } from "@/lib/api";
import { GraphData, GraphNode, GraphEdge } from "@/types";

export default function InvestigationGraphPage() {
  const params = useParams();
  const id = params.id as string;

  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [minConfidence, setMinConfidence] = useState(0);
  const [selectedTypeFilter, setSelectedTypeFilter] = useState<string>("ALL");

  useEffect(() => {
    getInvestigationGraph(id)
      .then((data) => {
        setGraphData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  const filteredNodes = graphData.nodes.filter((node) => {
    if (node.confidence < minConfidence) return false;
    if (selectedTypeFilter !== "ALL" && node.entity_type !== selectedTypeFilter) return false;
    return true;
  });

  const nodeIds = new Set(filteredNodes.map((n) => n.id));
  const filteredEdges = graphData.edges.filter(
    (e) => nodeIds.has(e.source) && nodeIds.has(e.target) && e.confidence >= minConfidence
  );

  const entityTypes = Array.from(new Set(graphData.nodes.map((n) => n.entity_type)));

  // Calculate layout coordinates for SVG rendering
  const width = 800;
  const height = 500;
  const radius = Math.min(width, height) / 2.5;
  const centerX = width / 2;
  const centerY = height / 2;

  const nodePositions = new Map<string, { x: number; y: number }>();
  filteredNodes.forEach((node, idx) => {
    const angle = (idx / (filteredNodes.length || 1)) * 2 * Math.PI;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    nodePositions.set(node.id, { x, y });
  });

  return (
    <div className="space-y-4">
      {/* Header & Controls */}
      <div className="p-4 rounded-xl bg-surface border border-border flex flex-wrap items-center justify-between gap-4 text-xs">
        <div className="flex items-center gap-3">
          <Link
            href={`/investigations/${id}`}
            className="p-1.5 rounded-lg bg-background border border-border hover:bg-surfaceHover text-slate-300 transition"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-base font-bold text-white flex items-center gap-2">
              <Network className="w-4 h-4 text-primary" />
              <span>Interactive Relationship Graph</span>
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">
              Showing {filteredNodes.length} nodes and {filteredEdges.length} edges
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">Type:</span>
            <select
              value={selectedTypeFilter}
              onChange={(e) => setSelectedTypeFilter(e.target.value)}
              className="px-2.5 py-1 rounded bg-background border border-border text-slate-200 font-mono focus:outline-none"
            >
              <option value="ALL">ALL TYPES</option>
              {entityTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-400">Min Confidence:</span>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={minConfidence}
              onChange={(e) => setMinConfidence(Number(e.target.value))}
              className="w-24 accent-primary"
            />
            <span className="font-mono text-slate-200 w-8">{minConfidence}%</span>
          </div>
        </div>
      </div>

      {/* Graph Visual Canvas & Node Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Canvas */}
        <div className="lg:col-span-3 h-[560px] bg-surface rounded-xl border border-border relative overflow-hidden flex items-center justify-center p-4">
          {loading ? (
            <div className="text-slate-500 text-sm">Loading intelligence graph...</div>
          ) : filteredNodes.length === 0 ? (
            <div className="text-slate-500 text-sm">No graph entities match the active filters.</div>
          ) : (
            <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
              {/* Render Edges */}
              {filteredEdges.map((edge) => {
                const sourcePos = nodePositions.get(edge.source);
                const targetPos = nodePositions.get(edge.target);
                if (!sourcePos || !targetPos) return null;

                return (
                  <g key={edge.id}>
                    <line
                      x1={sourcePos.x}
                      y1={sourcePos.y}
                      x2={targetPos.x}
                      y2={targetPos.y}
                      stroke="#334155"
                      strokeWidth="1.5"
                      strokeDasharray="4,2"
                    />
                    <text
                      x={(sourcePos.x + targetPos.x) / 2}
                      y={(sourcePos.y + targetPos.y) / 2 - 4}
                      fill="#64748b"
                      fontSize="9"
                      textAnchor="middle"
                      fontFamily="monospace"
                    >
                      {edge.label}
                    </text>
                  </g>
                );
              })}

              {/* Render Nodes */}
              {filteredNodes.map((node) => {
                const pos = nodePositions.get(node.id);
                if (!pos) return null;
                const isSelected = selectedNode?.id === node.id;

                const nodeColors: Record<string, string> = {
                  DOMAIN: "#0284c7",
                  SUBDOMAIN: "#38bdf8",
                  IP: "#10b981",
                  EMAIL: "#a855f7",
                  USERNAME: "#f59e0b",
                  URL: "#ec4899",
                  TECHNOLOGY: "#6366f1",
                };
                const color = nodeColors[node.entity_type] || "#64748b";

                return (
                  <g
                    key={node.id}
                    className="cursor-pointer transition-transform hover:scale-110"
                    onClick={() => setSelectedNode(node)}
                  >
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r={isSelected ? 18 : 14}
                      fill="#0f172a"
                      stroke={color}
                      strokeWidth={isSelected ? 3 : 2}
                    />
                    <circle cx={pos.x} cy={pos.y} r="4" fill={color} />
                    <text
                      x={pos.x}
                      y={pos.y + 24}
                      fill="#e2e8f0"
                      fontSize="10"
                      textAnchor="middle"
                      fontFamily="monospace"
                    >
                      {node.label.length > 18 ? node.label.slice(0, 15) + "..." : node.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          )}
        </div>

        {/* Node Inspector Drawer */}
        <div className="bg-surface rounded-xl border border-border p-4 space-y-4 text-xs">
          <div className="flex items-center gap-2 border-b border-border pb-2.5">
            <Info className="w-4 h-4 text-primary" />
            <h2 className="font-semibold text-white">Entity Inspector</h2>
          </div>

          {selectedNode ? (
            <div className="space-y-3">
              <div>
                <span className="text-[10px] text-slate-500 uppercase font-mono">Entity Type</span>
                <div className="font-mono text-primary-light font-bold">{selectedNode.entity_type}</div>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase font-mono">Canonical Value</span>
                <div className="font-mono text-slate-200 break-all bg-background p-2 rounded border border-border mt-0.5">
                  {selectedNode.label}
                </div>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase font-mono">Confidence Level</span>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex-1 h-2 rounded-full bg-background border border-border overflow-hidden">
                    <div
                      className="h-full bg-primary"
                      style={{ width: `${selectedNode.confidence}%` }}
                    />
                  </div>
                  <span className="font-mono text-slate-300 font-bold">{selectedNode.confidence}%</span>
                </div>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 uppercase font-mono">Attributes & Metadata</span>
                <pre className="text-[10px] font-mono text-slate-400 bg-background p-2 rounded border border-border overflow-x-auto mt-1 max-h-40">
                  {JSON.stringify(selectedNode.meta_info || {}, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <div className="py-12 text-center text-slate-500">
              Click on any node in the relationship graph to inspect its properties and connections.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
