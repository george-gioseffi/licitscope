import { cn } from "@/lib/utils";

interface ProgressProps {
  value: number; // 0..1
  tone?: "brand" | "amber" | "rose" | "mint";
  className?: string;
  label?: string;
}

const TONE_CLASS: Record<string, string> = {
  brand: "bg-brand-500",
  amber: "bg-amber-400",
  rose: "bg-rose-500",
  mint: "bg-emerald-400",
};

export function Progress({ value, tone = "brand", className, label }: ProgressProps) {
  const pct = Math.max(0, Math.min(1, value ?? 0)) * 100;
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="relative h-1.5 flex-1 overflow-hidden rounded-full bg-ink-800">
        <div
          className={cn("absolute inset-y-0 left-0 rounded-full", TONE_CLASS[tone])}
          style={{ width: `${pct}%` }}
        />
      </div>
      {label && <span className="text-[11px] tabular-nums text-ink-300">{label}</span>}
    </div>
  );
}
