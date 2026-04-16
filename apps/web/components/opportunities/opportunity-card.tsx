import Link from "next/link";
import { AlertTriangle, Building2, CalendarClock, MapPin } from "lucide-react";
import type { OpportunitySummary } from "@/lib/types";
import { ModalityBadge, StatusBadge } from "./modality-badge";
import { Badge } from "@/components/ui/badge";
import { formatCompactBRL, formatDate, daysUntil } from "@/lib/utils";

export function OpportunityCard({ opp }: { opp: OpportunitySummary }) {
  const closesIn = daysUntil(opp.proposals_close_at);
  const highRisk = (opp.risk_score ?? 0) >= 0.7;

  return (
    <Link
      href={`/opportunities/${opp.id}`}
      className="group flex h-full flex-col gap-3 rounded-xl border border-ink-800 bg-ink-900/60 p-5 transition hover:border-brand-500/50 hover:bg-ink-900"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 flex-1 flex-col gap-2">
          <div className="flex flex-wrap items-center gap-1.5">
            <ModalityBadge value={opp.modality} />
            <StatusBadge value={opp.status} />
            {opp.category && <Badge tone="outline">{opp.category}</Badge>}
            {highRisk && (
              <Badge tone="rose" title={`Risco heurístico ${Math.round((opp.risk_score ?? 0) * 100)}%`}>
                <AlertTriangle size={10} /> risco alto
              </Badge>
            )}
          </div>
          <h3 className="line-clamp-2 text-[14px] font-medium leading-snug text-ink-50 group-hover:text-white">
            {opp.title}
          </h3>
        </div>
        <div className="shrink-0 text-right">
          <div className="text-[10px] uppercase tracking-widest text-ink-400">Estimado</div>
          <div className="text-[15px] font-semibold tabular-nums text-ink-100">
            {formatCompactBRL(opp.estimated_value ?? null)}
          </div>
        </div>
      </div>

      <div className="mt-auto flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px] text-ink-400">
        {opp.agency?.name && (
          <span className="inline-flex items-center gap-1">
            <Building2 size={12} />
            <span className="line-clamp-1 max-w-[28ch]">{opp.agency.name}</span>
          </span>
        )}
        {opp.state && (
          <span className="inline-flex items-center gap-1">
            <MapPin size={12} /> {opp.city ?? ""} / {opp.state}
          </span>
        )}
        <span className="inline-flex items-center gap-1">
          <CalendarClock size={12} /> Publicada {formatDate(opp.published_at)}
        </span>
        {closesIn !== null && opp.status !== "closed" && opp.status !== "cancelled" && (
          <span
            className={`inline-flex items-center gap-1 font-medium ${
              closesIn < 0
                ? "text-ink-500"
                : closesIn <= 5
                  ? "text-rose-300"
                  : closesIn <= 15
                    ? "text-amber-300"
                    : "text-emerald-300"
            }`}
          >
            {closesIn >= 0 ? `Fecha em ${closesIn}d` : `Fechou há ${-closesIn}d`}
          </span>
        )}
      </div>
    </Link>
  );
}

export function OpportunityCardSkeleton() {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-ink-800 bg-ink-900/40 p-5">
      <div className="skeleton h-4 w-24" />
      <div className="skeleton h-5 w-[80%]" />
      <div className="skeleton h-4 w-[60%]" />
    </div>
  );
}
