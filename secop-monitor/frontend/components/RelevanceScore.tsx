"use client";

import { cn } from "@/lib/utils";

interface RelevanceScoreProps {
  score: number;
  size?: "sm" | "md";
}

export default function RelevanceScore({
  score,
  size = "md",
}: RelevanceScoreProps) {
  const color =
    score >= 80
      ? "text-green-400 border-green-400/30 bg-green-400/10"
      : score >= 60
        ? "text-yellow-400 border-yellow-400/30 bg-yellow-400/10"
        : score >= 40
          ? "text-orange-400 border-orange-400/30 bg-orange-400/10"
          : "text-[#a3a3a3] border-[#262626] bg-[#141414]";

  return (
    <div
      className={cn(
        "inline-flex items-center justify-center rounded-full border font-bold",
        color,
        size === "sm" ? "h-8 w-8 text-xs" : "h-10 w-10 text-sm"
      )}
    >
      {score}
    </div>
  );
}
