export type TargetType = "EMAIL" | "USERNAME" | "DOMAIN" | "IP" | "URL";

export type InvestigationStatus =
  | "CREATED"
  | "QUEUED"
  | "RUNNING"
  | "PARTIAL"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED";

export type FindingSeverity = "INFO" | "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface InvestigationSummary {
  id: string;
  title: string;
  target_input: string;
  target_type: TargetType;
  status: InvestigationStatus;
  is_authorized: boolean;
  created_at: string;
  completed_at: string | null;
  entities_count: number;
  findings_count: number;
  risk_score: number | null;
}

export interface CollectorJob {
  id: string;
  investigation_id: string;
  collector_name: string;
  status: "PENDING" | "RUNNING" | "COMPLETED" | "FAILED" | "TIMED_OUT" | "SKIPPED";
  started_at: string | null;
  completed_at: string | null;
  items_count: number;
  execution_duration_ms: number | null;
  error_message: string | null;
}

export interface InvestigationDetail {
  id: string;
  title: string;
  description: string | null;
  target_input: string;
  target_type: TargetType;
  is_authorized: boolean;
  authorization_notes: string | null;
  status: InvestigationStatus;
  created_at: string;
  completed_at: string | null;
  collector_jobs: CollectorJob[];
  meta_info: Record<string, any>;
}

export interface GraphNode {
  id: string;
  label: string;
  entity_type: string;
  confidence: number;
  meta_info: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  confidence: number;
  reason: string;
  source_tool: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  severity?: FindingSeverity;
  source?: string;
}

export interface ScanComparison {
  baseline_investigation_id: string;
  current_investigation_id: string;
  risk_assessment: {
    baseline_score: number;
    current_score: number;
    risk_delta: number;
    trend: "INCREASED" | "DECREASED" | "UNCHANGED";
  };
  asset_changes: {
    new_assets_count: number;
    removed_assets_count: number;
    persistent_assets_count: number;
    new_assets: Array<{ type: string; value: string; display: string }>;
    removed_assets: Array<{ type: string; value: string; display: string }>;
  };
  findings_summary: {
    baseline_total: number;
    current_total: number;
    delta: number;
  };
}
