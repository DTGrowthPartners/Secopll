"use client";

import MetricsBar from "@/components/MetricsBar";
import ContractFeed from "@/components/ContractFeed";
import SyncStatus from "@/components/SyncStatus";

export default function DashboardPage() {
  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="mt-1 text-sm text-[#a3a3a3]">
            Monitoreo de oportunidades SECOP para DT Growth Partners
          </p>
        </div>
        <SyncStatus />
      </div>

      <div className="mt-6">
        <MetricsBar />
      </div>

      <ContractFeed />
    </div>
  );
}
