"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, FileText } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/ui/empty-state";
import {
  OpportunityCard,
  OpportunityCardSkeleton,
} from "@/components/opportunities/opportunity-card";
import { OpportunityFilters } from "@/components/filters/opportunity-filters";
import { formatNumber } from "@/lib/utils";

const PAGE_SIZE = 20;

export default function OpportunitiesPage() {
  return (
    <Suspense fallback={<OpportunityCardSkeleton />}>
      <OpportunitiesPageInner />
    </Suspense>
  );
}

function OpportunitiesPageInner() {
  const sp = useSearchParams();
  const router = useRouter();
  const params: Record<string, string> = {};
  sp.forEach((v, k) => (params[k] = v));

  const page = Math.max(1, Number(params.page || 1));

  const query = useQuery({
    queryKey: ["opps", params],
    queryFn: () => api.opportunities({ ...params, page, page_size: PAGE_SIZE }),
  });
  const facets = useQuery({
    queryKey: ["opp-facets", params],
    queryFn: () => api.opportunityFacets(params),
  });

  const total = query.data?.meta?.total ?? 0;
  const totalPages = query.data?.meta?.total_pages ?? 1;

  function go(targetPage: number) {
    const next = new URLSearchParams(sp);
    if (targetPage <= 1) next.delete("page");
    else next.set("page", String(targetPage));
    router.push(`/opportunities?${next.toString()}`);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Feed de licitações"
        title="Licitações públicas"
        description="Filtre, ordene e explore licitações ativas e recentes com sinais de risco, prazos e contexto do órgão."
      />

      <OpportunityFilters
        modalities={(facets.data?.modalities ?? []).map((m) => ({
          value: m.value,
          label: m.label,
          count: m.count,
        }))}
        statuses={(facets.data?.statuses ?? []).map((m) => ({
          value: m.value,
          label: m.label.replace("_", " "),
          count: m.count,
        }))}
        categories={(facets.data?.categories ?? []).map((m) => ({
          value: m.value,
          label: m.label,
          count: m.count,
        }))}
      />

      <div className="flex items-center justify-between text-xs text-ink-400">
        <span>
          {query.isLoading
            ? "Carregando…"
            : `${formatNumber(total)} licitações · página ${page} de ${Math.max(1, totalPages)}`}
        </span>
        <Link href="/watchlists" className="text-brand-300 hover:text-brand-200">
          Salvar como watchlist →
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {query.isLoading &&
          Array.from({ length: 6 }).map((_, i) => <OpportunityCardSkeleton key={i} />)}
        {!query.isLoading && !query.data?.items?.length && (
          <div className="md:col-span-2">
            <EmptyState
              icon={<FileText />}
              title="Nada encontrado com esses filtros"
              description="Tente ampliar o período, remover a categoria ou o estado."
            />
          </div>
        )}
        {query.data?.items?.map((o) => <OpportunityCard key={o.id} opp={o} />)}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            disabled={page <= 1}
            onClick={() => go(page - 1)}
            className="inline-flex h-9 items-center gap-1 rounded-md px-3 text-xs text-ink-200 ring-1 ring-ink-700 hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <ChevronLeft size={14} /> Anterior
          </button>
          <span className="text-xs tabular-nums text-ink-400">
            {page} / {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => go(page + 1)}
            className="inline-flex h-9 items-center gap-1 rounded-md px-3 text-xs text-ink-200 ring-1 ring-ink-700 hover:bg-ink-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Próxima <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
