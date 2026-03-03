import type { paths } from "./generated/schema";

export type ApiPaths = paths;

export interface AuditEvent {
  event_id: string;
  actor_id: string;
  actor_name: string;
  action: string;
  resource_type: string;
  resource_id: string;
  ip?: string | null;
  user_agent?: string | null;
  result: "success" | "failure";
  trace_id: string;
  occurred_at: string;
}

export interface ReportQuery {
  report_code: string;
  start_date: string;
  end_date: string;
  group_by?: string;
  filters?: Record<string, string | number | boolean>;
  page?: number;
  page_size?: number;
}
