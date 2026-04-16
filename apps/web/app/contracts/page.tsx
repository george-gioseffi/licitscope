"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, BarChart3 } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { PriceRange } from "@/components/charts/price-range";
import { formatBRL, formatCompactBRL, formatDate } from "@/lib/utils";

export default function ContractsPage() {
  const contracts = useQuery({
    queryKey: ["contracts"],
    queryFn: () => api.contracts({ page_size: 30 }),
  });
  const pricing = useQuery({ queryKey: ["pricing"], queryFn: () => api.pricing() });

  const anomalyCount = (pricing.data ?? []).filter((p) => p.anomaly_flag).length;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Contratos & preços"
        title="Inteligência de preços e histórico de contratos"
        description="Compare preços praticados por órgãos, identifique dispersão anômala e explore os contratos assinados mais recentes."
      />

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 size={14} /> Dispersão de preços por CATMAT/CATSER
              </CardTitle>
              <CardDescription>
                Percentis e sinalização IQR-based — o traço claro marca a mediana;
                a faixa colorida cobre P25–P75.
              </CardDescription>
            </div>
            {!pricing.isLoading && (
              <div className="flex items-center gap-2 text-[11px]">
                <Badge tone="outline">{pricing.data?.length ?? 0} códigos</Badge>
                {anomalyCount > 0 && (
                  <Badge tone="rose">
                    <AlertTriangle size={10} />
                    {anomalyCount} com dispersão alta
                  </Badge>
                )}
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          {pricing.isLoading ? (
            <Skeleton className="h-40" />
          ) : (
            <table className="w-full text-xs">
              <thead>
                <tr className="text-left text-[10px] uppercase tracking-widest text-ink-400">
                  <th className="px-2 py-2">Código</th>
                  <th className="px-2 py-2">Descrição amostra</th>
                  <th className="px-2 py-2 text-right">Obs.</th>
                  <th className="px-2 py-2 text-right">Mín</th>
                  <th className="px-2 py-2 text-right">Mediana</th>
                  <th className="px-2 py-2 text-right">Máx</th>
                  <th className="w-[160px] px-2 py-2">Distribuição</th>
                  <th className="px-2 py-2 text-right">Sinal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-800">
                {pricing.data?.map((p) => (
                  <tr key={p.catmat_or_catser} className="text-ink-200">
                    <td className="px-2 py-2 font-mono text-[11px] text-ink-400">
                      {p.catmat_or_catser}
                    </td>
                    <td className="px-2 py-2">{p.description_sample}</td>
                    <td className="px-2 py-2 text-right tabular-nums">{p.observations}</td>
                    <td className="px-2 py-2 text-right tabular-nums text-ink-400">
                      {formatBRL(p.min_unit_price)}
                    </td>
                    <td className="px-2 py-2 text-right font-medium tabular-nums text-ink-50">
                      {formatBRL(p.median_unit_price)}
                    </td>
                    <td className="px-2 py-2 text-right tabular-nums text-ink-400">
                      {formatBRL(p.max_unit_price)}
                    </td>
                    <td className="px-2 py-2">
                      <PriceRange
                        min={p.min_unit_price}
                        p25={p.p25_unit_price}
                        median={p.median_unit_price}
                        p75={p.p75_unit_price}
                        max={p.max_unit_price}
                        anomaly={p.anomaly_flag}
                      />
                    </td>
                    <td className="px-2 py-2 text-right">
                      {p.anomaly_flag ? (
                        <Badge tone="rose">
                          <AlertTriangle size={10} /> dispersão alta
                        </Badge>
                      ) : (
                        <Badge tone="mint">normal</Badge>
                      )}
                    </td>
                  </tr>
                ))}
                {pricing.data?.length === 0 && (
                  <tr>
                    <td colSpan={8} className="py-6 text-center text-ink-400">
                      Sem observações de preço suficientes — rode mais ingestões para
                      popular a base de contratos.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Contratos recentes</CardTitle>
          <CardDescription>Últimos contratos assinados com fornecedores</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="divide-y divide-ink-800">
            {contracts.isLoading &&
              Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="py-3">
                  <Skeleton />
                </div>
              ))}
            {contracts.data?.items?.map((c) => (
              <div key={c.id} className="grid grid-cols-12 items-center gap-3 py-3 text-sm">
                <div className="col-span-5 min-w-0">
                  <div className="truncate font-medium text-ink-100">
                    {c.object_description.slice(0, 110)}
                  </div>
                  <div className="text-[11px] text-ink-400">
                    Contrato {c.contract_number ?? "—"} · assinado em{" "}
                    {formatDate(c.signed_at)}
                  </div>
                </div>
                <div className="col-span-3 min-w-0 text-ink-200">
                  <div className="truncate text-[13px]">{c.agency?.name ?? "—"}</div>
                  <div className="text-[11px] text-ink-400">{c.agency?.state ?? ""}</div>
                </div>
                <div className="col-span-3 min-w-0 text-ink-200">
                  <div className="truncate text-[13px]">{c.supplier?.name ?? "—"}</div>
                  <div className="font-mono text-[11px] text-ink-400">
                    {c.supplier?.tax_id ?? ""}
                  </div>
                </div>
                <div className="col-span-1 text-right tabular-nums text-ink-100">
                  {formatCompactBRL(c.total_value ?? null)}
                </div>
              </div>
            ))}
            {!contracts.isLoading && !contracts.data?.items?.length && (
              <div className="py-6 text-center text-xs text-ink-400">
                Nenhum contrato registrado ainda.
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
