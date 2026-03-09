"use client";

import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  ExternalLink,
  DollarSign,
  Calendar,
  Clock,
  MapPin,
  Building2,
  FileText,
  Bot,
  Save,
} from "lucide-react";
import { useState } from "react";
import { useContract, useUpdateContract } from "@/lib/hooks";
import { formatCOPFull, formatDate } from "@/lib/utils";
import RelevanceScore from "@/components/RelevanceScore";
import CategoryBadge from "@/components/CategoryBadge";

type InternalStatus = "new" | "reviewing" | "applied" | "discarded";

const STATUS_OPTIONS: {
  value: InternalStatus;
  label: string;
  color: string;
}[] = [
  { value: "new", label: "Nuevo", color: "bg-blue-500" },
  { value: "reviewing", label: "En revision", color: "bg-yellow-500" },
  { value: "applied", label: "Aplicado", color: "bg-green-500" },
  { value: "discarded", label: "Descartado", color: "bg-red-500" },
];

export default function ContractDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const { data: contract, isLoading, isError } = useContract(id);
  const update = useUpdateContract(id);

  const [notes, setNotes] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl">
        <div className="h-96 animate-pulse rounded-lg border border-[#262626] bg-[#141414]" />
      </div>
    );
  }

  if (isError || !contract) {
    return (
      <div className="mx-auto max-w-3xl text-center">
        <p className="text-red-400">Contrato no encontrado</p>
        <button
          onClick={() => router.push("/")}
          className="mt-4 text-sm text-brand-blue hover:underline"
        >
          Volver al dashboard
        </button>
      </div>
    );
  }

  const isPrivateUrl =
    contract.secop_url && contract.secop_url.includes("Login/Index");
  const currentNotes = notes ?? contract.notes ?? "";

  return (
    <div className="mx-auto max-w-3xl">
      <button
        onClick={() => router.push("/")}
        className="mb-4 flex items-center gap-1 text-sm text-[#a3a3a3] hover:text-[#ededed]"
      >
        <ArrowLeft size={16} />
        Volver al dashboard
      </button>

      <div className="rounded-lg border border-[#262626] bg-[#141414] p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <CategoryBadge category={contract.dt_service_category} />
            {contract.dt_service_tags?.map((tag) =>
              tag !== contract.dt_service_category ? (
                <CategoryBadge key={tag} category={tag} />
              ) : null
            )}
          </div>
          <RelevanceScore score={contract.relevance_score} size="md" />
        </div>

        <h1 className="mt-4 text-lg font-bold leading-snug">
          {contract.title}
        </h1>

        {contract.description && (
          <p className="mt-2 text-sm text-[#a3a3a3]">{contract.description}</p>
        )}

        {contract.classification_reason && (
          <div className="mt-4 flex items-start gap-2 rounded bg-[#1a1a2e] p-3">
            <Bot size={16} className="mt-0.5 shrink-0 text-brand-blue" />
            <p className="text-sm text-[#a3a3a3]">
              {contract.classification_reason}
            </p>
          </div>
        )}
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <DetailCard
          icon={<Building2 size={16} />}
          label="Entidad"
          value={contract.entity_name || "No disponible"}
          sub={contract.entity_nit ? `NIT: ${contract.entity_nit}` : undefined}
        />
        <DetailCard
          icon={<MapPin size={16} />}
          label="Ubicacion"
          value={
            [contract.city, contract.department].filter(Boolean).join(", ") ||
            "No disponible"
          }
        />
        <DetailCard
          icon={<DollarSign size={16} />}
          label="Valor estimado"
          value={formatCOPFull(contract.estimated_value)}
        />
        <DetailCard
          icon={<FileText size={16} />}
          label="Modalidad"
          value={contract.modality || "No disponible"}
          sub={contract.contract_type || undefined}
        />
        <DetailCard
          icon={<Calendar size={16} />}
          label="Publicado"
          value={formatDate(contract.published_at)}
        />
        <DetailCard
          icon={<Clock size={16} />}
          label="Fecha limite"
          value={formatDate(contract.deadline_at)}
        />
      </div>

      <div className="mt-4 rounded-lg border border-[#262626] bg-[#141414] p-6">
        <h2 className="mb-3 text-sm font-semibold">Estado interno</h2>

        <div className="flex flex-wrap gap-2">
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              onClick={() => update.mutate({ internal_status: opt.value })}
              disabled={update.isPending}
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
                contract.internal_status === opt.value
                  ? `${opt.color} text-white`
                  : "bg-[#262626] text-[#a3a3a3] hover:bg-[#363636]"
              }`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  contract.internal_status === opt.value
                    ? "bg-white"
                    : opt.color
                }`}
              />
              {opt.label}
            </button>
          ))}
        </div>

        <div className="mt-4">
          <label className="mb-1.5 block text-xs text-[#a3a3a3]">
            Asignado a
          </label>
          <input
            type="text"
            defaultValue={contract.assigned_to || ""}
            onBlur={(e) => update.mutate({ assigned_to: e.target.value })}
            placeholder="Nombre del responsable..."
            className="w-full rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-sm text-[#ededed] placeholder-[#525252] focus:border-brand-blue focus:outline-none"
          />
        </div>

        <div className="mt-4">
          <label className="mb-1.5 block text-xs text-[#a3a3a3]">Notas</label>
          <textarea
            value={currentNotes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notas internas del equipo..."
            rows={4}
            className="w-full resize-none rounded border border-[#262626] bg-[#0a0a0a] px-3 py-2 text-sm text-[#ededed] placeholder-[#525252] focus:border-brand-blue focus:outline-none"
          />
          <button
            onClick={() => update.mutate({ notes: currentNotes })}
            disabled={update.isPending}
            className="mt-2 flex items-center gap-1 rounded bg-brand-blue px-3 py-1.5 text-xs font-medium text-white hover:bg-[#2563eb] disabled:opacity-50"
          >
            <Save size={12} />
            Guardar notas
          </button>
        </div>
      </div>

      {contract.secop_url && !isPrivateUrl && (
        <div className="mt-4">
          <a
            href={contract.secop_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex w-full items-center justify-center gap-2 rounded-lg border border-brand-blue bg-brand-blue/10 py-3 text-sm font-medium text-brand-blue hover:bg-brand-blue/20"
          >
            <ExternalLink size={16} />
            Ver proceso completo en SECOP
          </a>
        </div>
      )}
    </div>
  );
}

function DetailCard({
  icon,
  label,
  value,
  sub,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="rounded-lg border border-[#262626] bg-[#141414] p-4">
      <div className="flex items-center gap-2 text-xs text-[#a3a3a3]">
        {icon}
        {label}
      </div>
      <p className="mt-1 text-sm font-semibold">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-[#525252]">{sub}</p>}
    </div>
  );
}