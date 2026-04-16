"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Skeleton } from "@/components/ui/skeleton";
import { formatDateTime } from "@/lib/utils";

const STATUS_TONE: Record<string, "mint" | "brand" | "amber" | "rose" | "default"> = {
  success: "mint",
  running: "brand",
  partial: "amber",
  failed: "rose",
};

export default function HealthPage() {
  const q = useQuery({ queryKey: ["source-health"], queryFn: api.sourcesHealth });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Infra & fontes"
        title="Saúde das integrações"
        description="Status e frescor das últimas execuções de ingestão, por fonte. Uma execução marcada como 'partial' usou o snapshot de fixtures como fallback depois que a fonte ao vivo falhou."
      />

      {q.isLoading && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} className="h-52" />
          ))}
        </div>
      )}

      {!q.isLoading && !q.data?.sources?.length && (
        <EmptyState
          icon={<Activity />}
          title="Nenhuma execução registrada ainda"
          description="Rode uma ingestão para popular este painel:"
          action={
            <code className="rounded bg-ink-800 px-2 py-1 font-mono text-[11px] text-ink-200">
              python -m app.scripts.run_ingestion
            </code>
          }
        />
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {q.data?.sources.map((s) => (
          <Card key={s.source}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="font-mono uppercase">{s.source}</CardTitle>
                <Badge tone={s.last_success ? "mint" : "amber"}>
                  {s.last_success ? "recente" : "sem sucesso recente"}
                </Badge>
              </div>
              <CardDescription>
                Último sucesso: {formatDateTime(s.last_success)}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {s.runs.length === 0 ? (
                <p className="text-xs text-ink-400">Nenhuma execução registrada para esta fonte.</p>
              ) : (
                <>
                  <div className="mb-2 grid grid-cols-12 gap-3 text-[10px] uppercase tracking-widest text-ink-500">
                    <span className="col-span-3">Quando</span>
                    <span className="col-span-2">Status</span>
                    <span className="col-span-2 text-right">Fetched</span>
                    <span className="col-span-2 text-right">Created</span>
                    <span className="col-span-2 text-right">Updated</span>
                    <span className="col-span-1 text-right">Failed</span>
                  </div>
                  <ul className="flex flex-col divide-y divide-ink-800">
                    {s.runs.map((r) => (
                      <li
                        key={r.id}
                        className="grid grid-cols-12 items-center gap-3 py-2 text-xs"
                      >
                        <span className="col-span-3 tabular-nums text-ink-300">
                          {formatDateTime(r.finished_at ?? r.started_at)}
                        </span>
                        <span className="col-span-2">
                          <Badge tone={STATUS_TONE[r.status] ?? "default"}>{r.status}</Badge>
                        </span>
                        <span className="col-span-2 text-right tabular-nums text-ink-200">
                          {r.fetched}
                        </span>
                        <span className="col-span-2 text-right tabular-nums text-ink-200">
                          {r.created}
                        </span>
                        <span className="col-span-2 text-right tabular-nums text-ink-200">
                          {r.updated}
                        </span>
                        <span
                          className={`col-span-1 text-right tabular-nums ${
                            r.failed > 0 ? "text-rose-300" : "text-ink-400"
                          }`}
                        >
                          {r.failed}
                        </span>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
