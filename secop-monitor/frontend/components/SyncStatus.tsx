"use client";

import { RefreshCw, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { useSyncStatus, useTriggerSync } from "@/lib/hooks";
import { timeAgo } from "@/lib/utils";

export default function SyncStatus() {
  const { data } = useSyncStatus();
  const trigger = useTriggerSync();

  const isRunning = data?.status === "running";

  return (
    <div className="flex items-center gap-3 text-xs text-[#a3a3a3]">
      <div className="flex items-center gap-1.5">
        {isRunning ? (
          <Loader2 size={14} className="animate-spin text-brand-blue" />
        ) : data?.status === "success" ? (
          <CheckCircle size={14} className="text-green-400" />
        ) : data?.status === "error" ? (
          <AlertCircle size={14} className="text-red-400" />
        ) : (
          <CheckCircle size={14} className="text-[#525252]" />
        )}
        <span>
          {isRunning
            ? "Sincronizando..."
            : data?.last_sync
              ? `Ultima sync: ${timeAgo(data.last_sync)}`
              : "Sin sincronizaciones"}
        </span>
      </div>

      <button
        onClick={() => trigger.mutate("SECOP_II")}
        disabled={trigger.isPending || isRunning}
        className="flex items-center gap-1 rounded bg-[#262626] px-2 py-1 text-[#ededed] hover:bg-[#363636] disabled:opacity-50"
      >
        <RefreshCw size={12} className={trigger.isPending ? "animate-spin" : ""} />
        Sync
      </button>
    </div>
  );
}
