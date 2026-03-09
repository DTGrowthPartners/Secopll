"use client";

import { BarChart3, DollarSign, TrendingUp, Target } from "lucide-react";
import { useDashboardStats } from "@/lib/hooks";
import { formatCOP } from "@/lib/utils";

interface MetricCardProps {
  label: string;
  value: string;
  icon: React.ReactNode;
}

function MetricCard({ label, value, icon }: MetricCardProps) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-[#262626] bg-[#141414] p-4">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-blue/10 text-brand-blue">
        {icon}
      </div>
      <div>
        <p className="text-sm text-[#a3a3a3]">{label}</p>
        <p className="text-xl font-bold">{value}</p>
      </div>
    </div>
  );
}

export default function MetricsBar() {
  const { data, isLoading } = useDashboardStats();

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div
            key={i}
            className="h-[76px] animate-pulse rounded-lg border border-[#262626] bg-[#141414]"
          />
        ))}
      </div>
    );
  }

  const rate =
    data.total_contracts > 0
      ? ((data.relevant_contracts / data.total_contracts) * 100).toFixed(1)
      : "0";

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        label="Contratos relevantes"
        value={data.relevant_contracts.toLocaleString("es-CO")}
        icon={<Target size={20} />}
      />
      <MetricCard
        label="Valor total oportunidades"
        value={formatCOP(data.total_value_cop)}
        icon={<DollarSign size={20} />}
      />
      <MetricCard
        label="Nuevos esta semana"
        value={data.new_this_week.toLocaleString("es-CO")}
        icon={<TrendingUp size={20} />}
      />
      <MetricCard
        label="Tasa de relevancia"
        value={`${rate}%`}
        icon={<BarChart3 size={20} />}
      />
    </div>
  );
}
