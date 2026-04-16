"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { OpportunityCard, OpportunityCardSkeleton } from "@/components/opportunities/opportunity-card";
import { OpportunityFilters } from "@/components/filters/opportunity-filters";
import { FileText } from "lucide-react";
import { formatNumber } from "@/lib/utils";

export default function OpportunitiesPage() {
  return (
    <Suspense fallback={<OpportunityCardSkeleton />}>
      <OpportunitiesPageInner />
    </Suspense>
  );
}

function OpportunitiesPageInner() {
  const sp = useSearchParams();
  const params: Record<string, string> = {};
  sp.forEach((v, k) => (params[k] = v));

  const query = useQuery({
    queryKey: ["opps", params],
    queryFn: () => api.opportunities({ ...params, page_size: 20 }),
  });

  const facets = useQuery({
    queryKey: ["opp-facets", params],
    queryFn: () => api.opportunityFacets(params),
  });

  const total = query.data?.meta?.total ?? 0;

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
            : `${formatNumber(total)} licitações encontradas`}
        </span>
        <Link href="/watchlists" className="text-brand-300 hover:text-brand-200">
          Salvar como watchlist →
        </Link>
      </div>

      <Card className="overflow-hidden">
        <div className="grid grid-cols-1 gap-0 divide-y divide-ink-800 md:grid-cols-2 md:gap-0 md:divide-x md:divide-y-0">
          <div className="flex flex-col divide-y divide-ink-800">
            {query.isLoading &&
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="p-1">
                  <OpportunityCardSkeleton />
                </div>
              ))}
            {!query.isLoading && !query.data?.items?.length && (
              <div className="p-4">
                <EmptyState
                  icon={<FileText />}
                  title="Nada encontrado com esses filtros"
                  description="Tente ampliar o período, remover a categoria ou o estado."
                />
              </div>
            )}
            {query.data?.items?.slice(0, Math.ceil((query.data.items.length || 0) / 2)).map((o) => (
              <div key={o.id} className="p-1">
                <OpportunityCard opp={o} />
              </div>
            ))}
          </div>
          <div className="flex flex-col divide-y divide-ink-800">
            {query.data?.items?.slice(Math.ceil((query.data.items.length || 0) / 2)).map((o) => (
              <div key={o.id} className="p-1">
                <OpportunityCard opp={o} />
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
