import Link from "next/link";
import type { OpportunitySummary } from "@/lib/types";
import { ModalityBadge, StatusBadge } from "./modality-badge";
import { formatCompactBRL, formatDate, daysUntil } from "@/lib/utils";

export function OpportunityRow({ opp }: { opp: OpportunitySummary }) {
  const closesIn = daysUntil(opp.proposals_close_at);
  return (
    <Link
      href={`/opportunities/${opp.id}`}
      className="grid grid-cols-12 items-center gap-3 border-b border-ink-800/70 px-4 py-3 text-sm transition hover:bg-ink-800/40"
    >
      <div className="col-span-6 min-w-0">
        <div className="line-clamp-1 font-medium text-ink-50">{opp.title}</div>
        <div className="mt-0.5 line-clamp-1 text-[11px] text-ink-400">
          {opp.agency?.name ?? "—"} · {opp.city ?? "—"} / {opp.state ?? "—"}
        </div>
      </div>
      <div className="col-span-2 flex flex-wrap items-center gap-1">
        <ModalityBadge value={opp.modality} />
      </div>
      <div className="col-span-1 text-ink-300">
        <StatusBadge value={opp.status} />
      </div>
      <div className="col-span-2 text-right tabular-nums text-ink-100">
        {formatCompactBRL(opp.estimated_value ?? null)}
      </div>
      <div className="col-span-1 text-right text-[11px] text-ink-400">
        {opp.proposals_close_at && closesIn !== null
          ? closesIn >= 0
            ? `${closesIn}d`
            : "fechada"
          : formatDate(opp.published_at)}
      </div>
    </Link>
  );
}

export function OpportunityTableHeader() {
  return (
    <div className="grid grid-cols-12 gap-3 border-b border-ink-800 bg-ink-900/60 px-4 py-2 text-[10px] uppercase tracking-widest text-ink-400">
      <div className="col-span-6">Objeto / Órgão</div>
      <div className="col-span-2">Modalidade</div>
      <div className="col-span-1">Situação</div>
      <div className="col-span-2 text-right">Valor estimado</div>
      <div className="col-span-1 text-right">Fechamento</div>
    </div>
  );
}
