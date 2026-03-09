"use client";

import Link from "next/link";
import {
  DollarSign,
  Calendar,
  Clock,
  ExternalLink,
  Eye,
  X,
  Bot,
} from "lucide-react";
import type { Contract } from "@/lib/types";
import { formatCOPFull, formatDate } from "@/lib/utils";
import RelevanceScore from "./RelevanceScore";
import CategoryBadge from "./CategoryBadge";
import { useUpdateContract } from "@/lib/hooks";

interface ContractCardProps {
  contract: Contract;
}

export default function ContractCard({ contract }: ContractCardProps) {
  const update = useUpdateContract(contract.id);

  const isPrivateUrl =
    contract.secop_url && contract.secop_url.includes("Login/Index");

  return (
    <div className="rounded-lg border border-[#262626] bg-[#141414] p-4 transition-colors hover:border-[#363636]">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <CategoryBadge category={contract.dt_service_category} />
          {contract.dt_service_tags?.map((tag) =>
            tag !== contract.dt_service_category ? (
              <CategoryBadge key={tag} category={tag} />
            ) : null
          )}
        </div>
        <RelevanceScore score={contract.relevance_score} />
      </div>

      <div className="mt-3">
        <p className="text-xs text-[#a3a3a3]">
          {contract.entity_name || "Entidad no disponible"}
          {contract.department && ` — ${contract.department}`}
        </p>
        <Link
          href={`/contracts/${contract.id}`}
          className="mt-1 block text-sm font-semibold leading-snug hover:text-brand-blue"
        >
          {contract.title}
        </Link>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-[#a3a3a3]">
        <span className="flex items-center gap-1">
          <DollarSign size={12} />
          {formatCOPFull(contract.estimated_value)}
        </span>
        <span className="flex items-center gap-1">
          <Calendar size={12} />
          {formatDate(contract.published_at)}
        </span>
        {contract.deadline_at && (
          <span className="flex items-center gap-1">
            <Clock size={12} />
            Limite: {formatDate(contract.deadline_at)}
          </span>
        )}
      </div>

      {contract.classification_reason && (
        <p className="mt-3 flex items-start gap-1.5 rounded bg-[#1a1a2e] p-2.5 text-xs text-[#a3a3a3]">
          <Bot size={14} className="mt-0.5 shrink-0 text-brand-blue" />
          {contract.classification_reason}
        </p>
      )}

      <div className="mt-3 flex items-center gap-2 border-t border-[#262626] pt-3">
        {contract.secop_url && !isPrivateUrl && (
          <a
            href={contract.secop_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 rounded bg-[#1a1a2e] px-2.5 py-1.5 text-xs text-brand-blue hover:bg-brand-blue/20"
          >
            <ExternalLink size={12} />
            Ver en SECOP
          </a>
        )}

        {contract.internal_status === "new" && (
          <>
            <button
              onClick={() => update.mutate({ internal_status: "reviewing" })}
              disabled={update.isPending}
              className="flex items-center gap-1 rounded bg-[#262626] px-2.5 py-1.5 text-xs text-[#ededed] hover:bg-[#363636]"
            >
              <Eye size={12} />
              Revisar
            </button>
            <button
              onClick={() => update.mutate({ internal_status: "discarded" })}
              disabled={update.isPending}
              className="flex items-center gap-1 rounded bg-[#262626] px-2.5 py-1.5 text-xs text-[#a3a3a3] hover:bg-red-500/20 hover:text-red-400"
            >
              <X size={12} />
              Descartar
            </button>
          </>
        )}

        {contract.internal_status === "reviewing" && (
          <span className="rounded bg-yellow-500/15 px-2.5 py-1 text-xs font-medium text-yellow-400">
            En revision
          </span>
        )}
        {contract.internal_status === "applied" && (
          <span className="rounded bg-green-500/15 px-2.5 py-1 text-xs font-medium text-green-400">
            Aplicado
          </span>
        )}
        {contract.internal_status === "discarded" && (
          <span className="rounded bg-red-500/15 px-2.5 py-1 text-xs font-medium text-red-400">
            Descartado
          </span>
        )}
      </div>
    </div>
  );
}
