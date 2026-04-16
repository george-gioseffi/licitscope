"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Users } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Stat } from "@/components/ui/stat";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { formatCompactBRL, formatDate, formatNumber } from "@/lib/utils";

export default function SupplierDetail() {
  const { id } = useParams<{ id: string }>();
  const sid = Number(id);
  const s = useQuery({ queryKey: ["supplier", sid], queryFn: () => api.supplier(sid) });
  const contracts = useQuery({
    queryKey: ["supplier-contracts", sid],
    queryFn: () => api.contracts({ supplier_id: sid, page_size: 20 }),
    enabled: !Number.isNaN(sid),
  });

  if (s.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-96" />
        <Skeleton className="h-6 w-2/3" />
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-[108px]" />
          ))}
        </div>
      </div>
    );
  }

  if (s.isError || !s.data) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-lg font-semibold">Fornecedor não encontrado</h1>
        <Link href="/suppliers" className="text-brand-300 hover:underline">
          ← Voltar aos fornecedores
        </Link>
      </div>
    );
  }

  const d = s.data;
  const location = [d.city, d.state].filter(Boolean).join(" / ") || "—";

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow={d.size ? d.size.toUpperCase() : "Fornecedor"}
        title={d.name}
        description={`${d.tax_id_type} ${d.tax_id} · ${location}`}
      />

      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        <Stat label="Contratos" value={formatNumber(d.contract_count)} accent="brand" />
        <Stat
          label="Valor contratado"
          value={formatCompactBRL(d.total_contracted_value)}
          accent="mint"
        />
        <Stat label="CNAE principal" value={d.main_cnae ?? "—"} accent="violet" />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Contratos recentes</CardTitle>
        </CardHeader>
        <CardContent>
          {contracts.isLoading && (
            <div className="flex flex-col gap-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} />
              ))}
            </div>
          )}
          {!contracts.isLoading && (contracts.data?.items?.length ?? 0) === 0 && (
            <EmptyState
              icon={<Users />}
              title="Sem contratos registrados"
              description="Este fornecedor não aparece em contratos capturados pelas ingestões atuais."
            />
          )}
          <div className="divide-y divide-ink-800">
            {contracts.data?.items?.map((c) => (
              <div key={c.id} className="grid grid-cols-12 items-center gap-3 py-3 text-sm">
                <div className="col-span-7 min-w-0">
                  <div className="truncate text-ink-100">
                    {c.object_description.slice(0, 120)}
                  </div>
                  <div className="text-[11px] text-ink-400">
                    {c.contract_number ?? "—"} · {formatDate(c.signed_at)}
                  </div>
                </div>
                <div className="col-span-3 min-w-0 truncate text-ink-300">
                  {c.agency?.name ?? "—"}
                </div>
                <div className="col-span-2 text-right tabular-nums text-ink-100">
                  {formatCompactBRL(c.total_value ?? null)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
