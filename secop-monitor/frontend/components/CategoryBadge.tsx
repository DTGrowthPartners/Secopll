"use client";

import { cn } from "@/lib/utils";

const CATEGORY_COLORS: Record<string, string> = {
  "Meta Ads": "bg-purple-500/15 text-purple-400 border-purple-500/30",
  "Desarrollo Web": "bg-blue-500/15 text-blue-400 border-blue-500/30",
  "Automatizaciones & IA": "bg-cyan-500/15 text-cyan-400 border-cyan-500/30",
  Chatbot: "bg-green-500/15 text-green-400 border-green-500/30",
  "Marketing Digital": "bg-pink-500/15 text-pink-400 border-pink-500/30",
  "Consultoría Digital": "bg-amber-500/15 text-amber-400 border-amber-500/30",
};

interface CategoryBadgeProps {
  category: string | null;
}

export default function CategoryBadge({ category }: CategoryBadgeProps) {
  if (!category || category === "No relevante") return null;

  const colorClass =
    CATEGORY_COLORS[category] ||
    "bg-[#262626] text-[#a3a3a3] border-[#363636]";

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        colorClass
      )}
    >
      {category}
    </span>
  );
}
