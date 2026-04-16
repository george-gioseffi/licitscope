"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDateTime } from "@/lib/utils";

export default function HealthPage() {
  const q = useQuery({ queryKey: ["source-health"], queryFn: api.sourcesHealth });

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Infra & fontes"
        title="Saúde das integrações"
        description="Status e frescor das últimas execuções de ingestão, por fonte."
      />
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
              <ul className="flex flex-col divide-y divide-ink-800">
                {s.runs.map((r) => (
                  <li key={r.id} className="grid grid-cols-12 items-center gap-3 py-2 text-xs">
                    <span className="col-span-3 text-ink-300">
                      {formatDateTime(r.finished_at ?? r.started_at)}
                    </span>
                    <span className="col-span-2">
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
                    </span>
                    <span className="col-span-2 text-ink-400">fetched {r.fetched}</span>
                    <span className="col-span-2 text-ink-400">created {r.created}</span>
                    <span className="col-span-2 text-ink-400">updated {r.updated}</span>
                    <span className="col-span-1 text-right text-ink-400">failed {r.failed}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        ))}
        {!q.isLoading && !q.data?.sources?.length && (
          <Card>
            <CardContent className="p-6 text-sm text-ink-400">
              Nenhuma execução registrada ainda. Rode <code className="rounded bg-ink-800 px-1">python -m app.scripts.run_ingestion</code>.
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
