"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Inbox } from "lucide-react";
import { useContracts, type ContractFilters } from "@/lib/hooks";
import ContractCard from "./ContractCard";
import FilterPanel from "./FilterPanel";

export default function ContractFeed() {
  const [filters, setFilters] = useState<ContractFilters>({
    page: 1,
    limit: 20,
    min_score: 0,
  });

  const { data, isLoading, isError } = useContracts(filters);

  return (
    <div className="mt-6 flex flex-col gap-6 lg:flex-row">
      {/* Sidebar filters */}
      <aside className="w-full shrink-0 lg:w-64">
        <FilterPanel filters={filters} onChange={setFilters} />
      </aside>

      {/* Feed */}
      <div className="flex-1">
        {isError && (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-center text-sm text-red-400">
            Error al cargar contratos. Verifica que el backend este corriendo.
          </div>
        )}

        {isLoading && (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="h-40 animate-pulse rounded-lg border border-[#262626] bg-[#141414]"
              />
            ))}
          </div>
        )}

        {data && data.items.length === 0 && (
          <div className="flex flex-col items-center justify-center rounded-lg border border-[#262626] bg-[#141414] py-16 text-[#a3a3a3]">
            <Inbox size={40} className="mb-3" />
            <p className="text-sm font-medium">No se encontraron contratos</p>
            <p className="mt-1 text-xs">
              Ajusta los filtros o espera la proxima sincronizacion
            </p>
          </div>
        )}

        {data && data.items.length > 0 && (
          <>
            <div className="mb-3 flex items-center justify-between text-xs text-[#a3a3a3]">
              <span>
                {data.total.toLocaleString("es-CO")} contratos encontrados
              </span>
              <span>
                Pagina {data.page} de {data.pages}
              </span>
            </div>

            <div className="space-y-3">
              {data.items.map((contract) => (
                <ContractCard key={contract.id} contract={contract} />
              ))}
            </div>

            {/* Pagination */}
            {data.pages > 1 && (
              <div className="mt-4 flex items-center justify-center gap-2">
                <button
                  onClick={() =>
                    setFilters((f) => ({ ...f, page: (f.page || 1) - 1 }))
                  }
                  disabled={data.page <= 1}
                  className="flex items-center gap-1 rounded bg-[#262626] px-3 py-1.5 text-xs text-[#ededed] hover:bg-[#363636] disabled:opacity-30"
                >
                  <ChevronLeft size={14} />
                  Anterior
                </button>
                <span className="text-xs text-[#a3a3a3]">
                  {data.page} / {data.pages}
                </span>
                <button
                  onClick={() =>
                    setFilters((f) => ({ ...f, page: (f.page || 1) + 1 }))
                  }
                  disabled={data.page >= data.pages}
                  className="flex items-center gap-1 rounded bg-[#262626] px-3 py-1.5 text-xs text-[#ededed] hover:bg-[#363636] disabled:opacity-30"
                >
                  Siguiente
                  <ChevronRight size={14} />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
