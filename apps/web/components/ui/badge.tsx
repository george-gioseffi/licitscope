import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const TONES = {
  default: "bg-ink-800 text-ink-200 ring-ink-700",
  brand: "bg-brand-600/20 text-brand-200 ring-brand-600/40",
  mint: "bg-emerald-500/15 text-emerald-200 ring-emerald-500/30",
  amber: "bg-amber-500/15 text-amber-200 ring-amber-500/30",
  rose: "bg-rose-500/15 text-rose-200 ring-rose-500/30",
  violet: "bg-violet-500/15 text-violet-200 ring-violet-500/30",
  outline: "bg-transparent text-ink-200 ring-ink-600",
} as const;

export function Badge({
  tone = "default",
  className,
  children,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: keyof typeof TONES }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-medium ring-1",
        TONES[tone],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
