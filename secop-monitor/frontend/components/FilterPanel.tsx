"use client";

import { Search, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import type { ContractFilters } from "@/lib/hooks";

const SERVICE_OPTIONS = [
  "Meta Ads",
  "Desarrollo Web",
  "Automatizaciones & IA",
  "Chatbot",
  "Marketing Digital",
  "Consultoría Digital",
];

const INTERNAL_STATUS_OPTIONS = [
  { value: "", label: "Todos" },
  { value: "new", label: "Nuevo" },
  { value: "reviewing", label: "Revisando" },
  { value: "applied", label: "Aplicado" },
  { value: "discarded", label: "Descartado" },
];

interface FilterPanelProps {
  filters: ContractFilters;
  onChange: (filters: ContractFilters) => void;
}

export default function FilterPanel({ filters, onChange }: FilterPanelProps) {
  const [open, setOpen] = useState(true);

  const set = (key: keyof ContractFilters, value: string | number) => {
    onChange({ ...filters, [key]: value || undefined, page: 1 });
  };

  return (
    <div className="rounded-lg border border-[#262626] bg-[#141414]">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between p-4 text-sm font-semibold"
      >
        <span className="flex items-center gap-2">
          <SlidersHorizontal size={16} />
          Filtros
        </span>
        <span className="text-xs text-[#a3a3a3]">{open ? "Ocultar" : "Mostrar"}</span>
      </button>

      {open && (
        <div className="space-y-4 border-t border-[#262626] p-4">
          {/* Search */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">Buscar</label>
            <div className="relative">
              <Search
                size={14}
                className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[#a3a3a3]"
              />
              <input
                type="text"
                placeholder="Titulo o descripcion..."
                value={filters.search || ""}
                onChange={(e) => set("search", e.target.value)}
                className="w-full rounded border border-[#262626] bg-[#0a0a0a] py-2 pl-8 pr-3 text-xs text-[#ededed] placeholder-[#525252] focus:border-brand-blue focus:outline-none"
              />
            </div>
          </div>

          {/* Min score */}
          <div>
            <label className="mb-1.5 flex items-center justify-between text-xs text-[#a3a3a3]">
              <span>Score minimo</span>
              <span className="font-mono text-[#ededed]">{filters.min_score || 0}</span>
            </label>
            <input
              type="range"
              min={0}
              max={100}
              step={5}
              value={filters.min_score || 0}
              onChange={(e) => set("min_score", Number(e.target.value))}
              className="w-full accent-brand-blue"
            />
          </div>

          {/* Service category */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Servicio DT
            </label>
            <select
              value={filters.service_category || ""}
              onChange={(e) => set("service_category", e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-xs text-[#ededed] focus:border-brand-blue focus:outline-none"
            >
              <option value="">Todos</option>
              {SERVICE_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Internal status */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Estado interno
            </label>
            <select
              value={filters.internal_status || ""}
              onChange={(e) => set("internal_status", e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-xs text-[#ededed] focus:border-brand-blue focus:outline-none"
            >
              {INTERNAL_STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Department */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Departamento
            </label>
            <input
              type="text"
              placeholder="Ej: Bogota, Antioquia..."
              value={filters.department || ""}
              onChange={(e) => set("department", e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-xs text-[#ededed] placeholder-[#525252] focus:border-brand-blue focus:outline-none"
            />
          </div>

          {/* Process status */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Estado del proceso
            </label>
            <select
              value={filters.status || ""}
              onChange={(e) => set("status", e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-xs text-[#ededed] focus:border-brand-blue focus:outline-none"
            >
              <option value="">Todos</option>
              <option value="Abierto">Abierto</option>
              <option value="Cerrado">Cerrado</option>
            </select>
          </div>

          {/* Date from */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Desde
            </label>
            <input
              type="date"
              value={filters.date_from || ""}
              onChange={(e) => set("date_from", e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-xs text-[#ededed] focus:border-brand-blue focus:outline-none"
            />
          </div>

          {/* Date to */}
          <div>
            <label className="mb-1.5 block text-xs text-[#a3a3a3]">
              Hasta
            </label>
            <input
              type="date"
              value={filters.date_to || ""}
              onChange={(e) => set("date_to", e.target.value)}
              className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-xs text-[#ededed] focus:border-brand-blue focus:outline-none"
            />
          </div>

          {/* Reset */}
          <button
            onClick={() => onChange({ page: 1, limit: 20, min_score: 0 })}
            className="w-full rounded border border-[#262626] py-2 text-xs text-[#a3a3a3] hover:border-[#363636] hover:text-[#ededed]"
          >
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
}
