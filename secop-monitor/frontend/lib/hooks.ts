"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchAPI } from "./api";
import type {
  Contract,
  PaginatedResponse,
  DashboardStats,
  SyncStatus,
} from "./types";

export interface ContractFilters {
  page?: number;
  limit?: number;
  min_score?: number;
  service_category?: string;
  status?: string;
  department?: string;
  date_from?: string;
  date_to?: string;
  internal_status?: string;
  search?: string;
  source?: string;
}

function buildQuery(filters: ContractFilters): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && value !== null) {
      params.set(key, String(value));
    }
  });
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function useContracts(filters: ContractFilters) {
  return useQuery({
    queryKey: ["contracts", filters],
    queryFn: () =>
      fetchAPI<PaginatedResponse<Contract>>(
        `/contracts${buildQuery(filters)}`
      ),
  });
}

export function useContract(id: string) {
  return useQuery({
    queryKey: ["contract", id],
    queryFn: () => fetchAPI<Contract>(`/contracts/${id}`),
    enabled: !!id,
  });
}

export function useUpdateContract(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Contract>) =>
      fetchAPI<Contract>(`/contracts/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contract", id] });
      qc.invalidateQueries({ queryKey: ["contracts"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard"],
    queryFn: () => fetchAPI<DashboardStats>("/dashboard/stats"),
  });
}

export function useSyncStatus() {
  return useQuery({
    queryKey: ["syncStatus"],
    queryFn: () => fetchAPI<SyncStatus | null>("/sync/status"),
    refetchInterval: 30000,
  });
}

export function useTriggerSync() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (source: string = "SECOP_II") =>
      fetchAPI<{ job_id: string }>(`/sync/trigger?source=${source}`, {
        method: "POST",
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["syncStatus"] });
    },
  });
}
