"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Building2 } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Stat } from "@/components/ui/stat";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCompactBRL, formatNumber } from "@/lib/utils";
import {
  OpportunityCard,
  OpportunityCardSkeleton,
} from "@/components/opportunities/opportunity-card";

export default function AgencyDetail() {
  const { id } = useParams<{ id: string }>();
  const aid = Number(id);

  const agency = useQuery({ queryKey: ["agency", aid], queryFn: () => api.agency(aid) });
  const opps = useQuery({
    queryKey: ["agency-opps", aid],
    queryFn: () => api.opportunities({ agency_id: aid, page_size: 10 }),
    enabled: !Number.isNaN(aid),
  });

  if (agency.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-96" />
        <Skeleton className="h-6 w-2/3" />
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[108px]" />
          ))}
        </div>
      </div>
    );
  }

  if (agency.isError || !agency.data) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-lg font-semibold">Órgão não encontrado</h1>
        <Link href="/agencies" className="text-brand-300 hover:underline">
          ← Voltar aos órgãos
        </Link>
      </div>
    );
  }

  const a = agency.data;
  const location = [a.city, a.state].filter(Boolean).join(" / ") || "—";

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow={a.sphere ? a.sphere.toUpperCase() : "Órgão contratante"}
        title={a.name}
        description={`CNPJ ${a.cnpj} · ${location}`}
      />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Stat label="Licitações totais" value={formatNumber(a.opportunity_count)} accent="brand" />
        <Stat
          label="Licitações ativas"
          value={formatNumber(a.active_opportunities)}
          accent="mint"
        />
        <Stat label="Contratos" value={formatNumber(a.contract_count)} accent="violet" />
        <Stat
          label="Valor contratado"
          value={formatCompactBRL(a.total_contracted_value)}
          accent="amber"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 size={14} /> Licitações recentes do órgão
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {opps.isLoading &&
              Array.from({ length: 4 }).map((_, i) => <OpportunityCardSkeleton key={i} />)}
            {!opps.isLoading && (opps.data?.items?.length ?? 0) === 0 && (
              <div className="md:col-span-2">
                <EmptyState
                  icon={<Building2 />}
                  title="Sem licitações recentes deste órgão"
                  description="O órgão está na base, mas não publicou nada capturado pelas ingestões mais recentes."
                />
              </div>
            )}
            {opps.data?.items?.map((o) => <OpportunityCard key={o.id} opp={o} />)}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Categorias principais</CardTitle>
          </CardHeader>
          <CardContent>
            {a.top_categories.length === 0 ? (
              <span className="text-xs text-ink-400">Sem histórico suficiente.</span>
            ) : (
              <ul className="flex flex-col divide-y divide-ink-800 text-sm">
                {a.top_categories.map((c) => (
                  <li key={c.category} className="flex items-center justify-between py-2">
                    <span className="text-ink-200">{c.category}</span>
                    <Badge tone="outline">{c.count}</Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
