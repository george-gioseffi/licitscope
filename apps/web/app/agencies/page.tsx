"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function AgenciesPage() {
  const q = useQuery({ queryKey: ["agencies"], queryFn: () => api.agencies({ page_size: 100 }) });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Órgãos contratantes"
        title="Órgãos e entidades"
        description="Explore os órgãos públicos que realizaram licitações, com seus perfis de atividade e distribuição por categoria."
      />
      <Card>
        <div className="divide-y divide-ink-800">
          <div className="grid grid-cols-12 gap-3 px-4 py-2 text-[10px] uppercase tracking-widest text-ink-400">
            <div className="col-span-5">Nome</div>
            <div className="col-span-2">CNPJ</div>
            <div className="col-span-2">Esfera</div>
            <div className="col-span-2">Localização</div>
            <div className="col-span-1 text-right">Fonte</div>
          </div>
          {q.isLoading &&
            Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="p-4">
                <Skeleton />
              </div>
            ))}
          {q.data?.items?.map((a) => (
            <Link
              key={a.id}
              href={`/agencies/${a.id}`}
              className="grid grid-cols-12 items-center gap-3 px-4 py-3 text-sm transition hover:bg-ink-800/30"
            >
              <div className="col-span-5 font-medium text-ink-50">{a.name}</div>
              <div className="col-span-2 font-mono text-[11px] text-ink-400">{a.cnpj}</div>
              <div className="col-span-2">
                {a.sphere && <Badge tone="outline">{a.sphere}</Badge>}
              </div>
              <div className="col-span-2 text-ink-300">
                {a.city ?? "—"} / {a.state ?? ""}
              </div>
              <div className="col-span-1 text-right font-mono text-[10px] uppercase text-ink-400">
                {a.source}
              </div>
            </Link>
          ))}
        </div>
      </Card>
    </div>
  );
}
