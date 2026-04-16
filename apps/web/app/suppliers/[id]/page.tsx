"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Stat } from "@/components/ui/stat";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCompactBRL, formatNumber } from "@/lib/utils";

export default function SupplierDetail() {
  const { id } = useParams<{ id: string }>();
  const sid = Number(id);
  const s = useQuery({ queryKey: ["supplier", sid], queryFn: () => api.supplier(sid) });
  const contracts = useQuery({
    queryKey: ["supplier-contracts", sid],
    queryFn: () => api.contracts({ supplier_id: sid, page_size: 20 }),
  });

  if (s.isLoading) return <Skeleton className="h-32" />;
  const d = s.data!;

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow={d.size ?? "Fornecedor"}
        title={d.name}
        description={`${d.tax_id_type} ${d.tax_id} · ${d.city ?? ""} / ${d.state ?? ""}`}
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
          <div className="divide-y divide-ink-800">
            {contracts.data?.items?.map((c) => (
              <div key={c.id} className="grid grid-cols-12 items-center gap-3 py-3 text-sm">
                <div className="col-span-8 truncate text-ink-100">
                  {c.object_description.slice(0, 120)}
                </div>
                <div className="col-span-2 text-ink-400">{c.agency?.name?.slice(0, 30) ?? "—"}</div>
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
