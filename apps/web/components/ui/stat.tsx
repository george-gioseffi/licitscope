import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatProps {
  label: string;
  value: string;
  trend?: number | null;
  hint?: string;
  accent?: "brand" | "mint" | "amber" | "rose" | "violet";
}

const ACCENTS: Record<string, string> = {
  brand: "from-brand-500/20 to-transparent",
  mint: "from-emerald-500/20 to-transparent",
  amber: "from-amber-500/20 to-transparent",
  rose: "from-rose-500/20 to-transparent",
  violet: "from-violet-500/20 to-transparent",
};

export function Stat({ label, value, trend, hint, accent = "brand" }: StatProps) {
  const T = trend ?? 0;
  const icon = T > 0 ? <ArrowUpRight size={14} /> : T < 0 ? <ArrowDownRight size={14} /> : <Minus size={14} />;
  const color =
    T > 0 ? "text-emerald-300" : T < 0 ? "text-rose-300" : "text-ink-300";
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border border-ink-800 bg-ink-900/70 p-5 shadow-card",
      )}
    >
      <div
        className={cn(
          "absolute inset-x-0 top-0 h-16 bg-gradient-to-b",
          ACCENTS[accent],
        )}
      />
      <div className="relative">
        <div className="text-[11px] uppercase tracking-wider text-ink-400">{label}</div>
        <div className="mt-2 text-2xl font-semibold tracking-tight text-ink-50">{value}</div>
        <div className="mt-1 flex items-center gap-2 text-xs">
          {trend !== null && trend !== undefined && (
            <span className={cn("inline-flex items-center gap-1", color)}>
              {icon}
              <span className="tabular-nums">
                {T > 0 ? "+" : ""}
                {trend}
              </span>
            </span>
          )}
          {hint && <span className="text-ink-400">· {hint}</span>}
        </div>
      </div>
    </div>
  );
}
