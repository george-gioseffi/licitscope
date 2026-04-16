"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function SuppliersPage() {
  const q = useQuery({ queryKey: ["suppliers"], queryFn: () => api.suppliers({ page_size: 100 }) });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Fornecedores"
        title="Empresas contratadas"
        description="Conheça os fornecedores vinculados a contratos já firmados com o setor público."
      />
      <Card>
        <div className="divide-y divide-ink-800">
          <div className="grid grid-cols-12 gap-3 px-4 py-2 text-[10px] uppercase tracking-widest text-ink-400">
            <div className="col-span-5">Razão social</div>
            <div className="col-span-2">CNPJ/CPF</div>
            <div className="col-span-2">Porte</div>
            <div className="col-span-2">Localização</div>
            <div className="col-span-1 text-right">CNAE</div>
          </div>
          {q.isLoading &&
            Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="p-4">
                <Skeleton />
              </div>
            ))}
          {q.data?.items?.map((s) => (
            <Link
              key={s.id}
              href={`/suppliers/${s.id}`}
              className="grid grid-cols-12 items-center gap-3 px-4 py-3 text-sm hover:bg-ink-800/30"
            >
              <div className="col-span-5">
                <div className="font-medium text-ink-50">{s.name}</div>
                {s.trade_name && <div className="text-[11px] text-ink-400">{s.trade_name}</div>}
              </div>
              <div className="col-span-2 font-mono text-[11px] text-ink-400">{s.tax_id}</div>
              <div className="col-span-2">{s.size && <Badge tone="outline">{s.size}</Badge>}</div>
              <div className="col-span-2 text-ink-300">
                {s.city ?? "—"} / {s.state ?? ""}
              </div>
              <div className="col-span-1 text-right font-mono text-[10px] text-ink-400">
                {s.main_cnae ?? "—"}
              </div>
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}
