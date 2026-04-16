"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Stat } from "@/components/ui/stat";
import { Skeleton } from "@/components/ui/skeleton";
import { TimeSeriesArea } from "@/components/charts/area-chart";
import { CompactBar } from "@/components/charts/bar-chart";
import { Donut } from "@/components/charts/donut-chart";
import { OpportunityCard, OpportunityCardSkeleton } from "@/components/opportunities/opportunity-card";
import { formatCompactBRL, formatDateTime } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["overview"],
    queryFn: () => api.overview(),
  });

  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        eyebrow="Visão executiva"
        title="Inteligência de compras públicas no Brasil"
        description="Painel consolidado de licitações, contratos e sinais de risco — alimentado pelo PNCP e enriquecido por heurísticas locais."
        actions={
          <Link
            href="/opportunities"
            className="inline-flex items-center gap-2 rounded-md bg-brand-600/20 px-3 py-1.5 text-xs font-medium text-brand-200 ring-1 ring-brand-600/40 hover:bg-brand-600/30"
          >
            Explorar licitações <ArrowRight size={14} />
          </Link>
        }
      />

      {/* KPIs */}
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {isLoading && Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[108px]" />)}
        {data?.kpis?.map((k, i) => (
          <Stat
            key={k.label}
            label={k.label}
            value={
              k.suffix === "BRL"
                ? formatCompactBRL(k.value)
                : Number.isInteger(k.value)
                  ? String(k.value)
                  : k.value.toFixed(2)
            }
            trend={k.trend ?? null}
            hint={k.description ?? undefined}
            accent={(["brand", "mint", "amber", "violet"] as const)[i % 4]}
          />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Publicações nos últimos 30 dias</CardTitle>
                <CardDescription>
                  Fluxo diário de novos editais nos órgãos monitorados
                </CardDescription>
              </div>
              <Badge tone="brand">
                <TrendingUp size={12} />
                PNCP
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[240px]" />
            ) : (
              <TimeSeriesArea data={data?.published_per_day ?? []} dataKey="count" />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mix por modalidade</CardTitle>
            <CardDescription>Distribuição das publicações recentes</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[240px]" />
            ) : (
              <Donut
                data={(data?.by_modality ?? []).map((m) => ({ name: m.category, value: m.count }))}
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Categories + states */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top categorias</CardTitle>
            <CardDescription>Volume de licitações enriquecidas</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[240px]" />
            ) : (
              <CompactBar
                layout="horizontal"
                data={(data?.by_category ?? []).slice(0, 8).map((c) => ({
                  name: c.category,
                  count: c.count,
                  value: c.total_value,
                }))}
                categoryKey="name"
                valueKey="count"
              />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Distribuição geográfica</CardTitle>
            <CardDescription>Publicações por UF</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <Skeleton className="h-[240px]" />
            ) : (
              <CompactBar
                data={(data?.by_state ?? []).slice(0, 12).map((s) => ({
                  name: s.state,
                  count: s.count,
                }))}
                categoryKey="name"
                valueKey="count"
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Top agencies */}
      <Card>
        <CardHeader>
          <CardTitle>Top órgãos contratantes</CardTitle>
          <CardDescription>
            Por volume de licitações, com valor total estimado acumulado
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-ink-800">
            {(data?.top_agencies ?? []).map((a) => (
              <Link
                key={String(a.agency_id)}
                href={a.agency_id ? `/agencies/${a.agency_id}` : "/agencies"}
                className="grid grid-cols-12 items-center gap-3 py-3 text-sm transition hover:bg-ink-800/30"
              >
                <div className="col-span-6 truncate font-medium text-ink-100">{a.name}</div>
                <div className="col-span-2 text-ink-400">{a.state ?? "—"}</div>
                <div className="col-span-2 tabular-nums text-ink-200">{a.count} licitações</div>
                <div className="col-span-2 text-right tabular-nums text-ink-300">
                  {formatCompactBRL(a.total_value)}
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent + source health */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Publicações recentes</CardTitle>
            <CardDescription>Últimas licitações capturadas pelas fontes</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {isLoading &&
              Array.from({ length: 4 }).map((_, i) => <OpportunityCardSkeleton key={i} />)}
            {data?.recent?.slice(0, 6).map((o) => <OpportunityCard key={o.id} opp={o} />)}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Fontes & ingestões</CardTitle>
            <CardDescription>Execuções recentes e status de integração</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="flex flex-col divide-y divide-ink-800">
              {(data?.source_health ?? []).slice(0, 8).map((r) => (
                <li key={r.id} className="flex items-center justify-between py-2.5 text-xs">
                  <span className="font-mono uppercase text-ink-200">{r.source}</span>
                  <span className="text-ink-400">{formatDateTime(r.finished_at ?? r.started_at)}</span>
                  <Badge
                    tone={
                      r.status === "success"
                        ? "mint"
                        : r.status === "running"
                          ? "brand"
                          : r.status === "partial"
                            ? "amber"
                            : "rose"
                    }
                  >
                    {r.status}
                  </Badge>
                </li>
              ))}
              {!isLoading && !data?.source_health?.length && (
                <li className="py-4 text-xs text-ink-400">Nenhuma execução registrada ainda.</li>
              )}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
