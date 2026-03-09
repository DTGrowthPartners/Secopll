export interface Contract {
  id: string;
  secop_id: string;
  source: "SECOP_I" | "SECOP_II";
  entity_name: string | null;
  entity_nit: string | null;
  department: string | null;
  city: string | null;
  title: string;
  description: string | null;
  contract_type: string | null;
  modality: string | null;
  estimated_value: number | null;
  duration_days: number | null;
  status: string | null;
  phase: string | null;
  published_at: string | null;
  deadline_at: string | null;
  last_updated_at: string | null;
  secop_url: string | null;
  category_code: string | null;
  relevance_score: number;
  dt_service_category: string | null;
  dt_service_tags: string[] | null;
  classification_reason: string | null;
  is_relevant: boolean;
  internal_status: "new" | "reviewing" | "applied" | "discarded";
  assigned_to: string | null;
  notes: string | null;
  notified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
}

export interface DashboardStats {
  total_contracts: number;
  relevant_contracts: number;
  new_this_week: number;
  total_value_cop: number;
  by_service: Record<string, number>;
  by_department: Record<string, number>;
  last_sync: string | null;
  pipeline: {
    new: number;
    reviewing: number;
    applied: number;
    discarded: number;
  };
}

export interface SyncStatus {
  status: string;
  last_sync: string | null;
}
