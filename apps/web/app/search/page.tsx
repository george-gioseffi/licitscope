"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { FormEvent, Suspense, useState } from "react";
import { Sparkles, SearchIcon, Lightbulb } from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { OpportunityCard, OpportunityCardSkeleton } from "@/components/opportunities/opportunity-card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";

const EXAMPLE_QUERIES = [
  "medicamentos da farmácia básica",
  "notebook para servidores públicos",
  "recapeamento asfáltico",
  "vigilância patrimonial armada",
  "merenda escolar",
  "consultoria de modernização",
];

export default function SearchPage() {
  return (
    <Suspense fallback={<OpportunityCardSkeleton />}>
      <SearchPageInner />
    </Suspense>
  );
}

function SearchPageInner() {
  const sp = useSearchParams();
  const router = useRouter();
  const q = sp.get("q") ?? "";
  const [draft, setDraft] = useState(q);

  const res = useQuery({
    queryKey: ["search", q],
    queryFn: () => api.search(q, 20),
    enabled: q.length >= 2,
  });

  function submit(e: FormEvent) {
    e.preventDefault();
    if (draft.trim().length < 2) return;
    router.push(`/search?q=${encodeURIComponent(draft.trim())}`);
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Busca semântica"
        title="Encontre licitações pelo sentido, não só pela palavra"
        description="Usamos TF-IDF offline para ranquear licitações por similaridade ao seu pedido — sem enviar nada para LLMs externos por padrão."
      />

      <form onSubmit={submit} className="flex gap-2">
        <div className="relative flex-1">
          <SearchIcon
            size={14}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-400"
          />
          <Input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="ex: 'hemodiálise credenciamento' ou 'locação de veículos'"
            className="pl-9"
          />
        </div>
        <Button type="submit">
          <Sparkles size={14} />
          Buscar
        </Button>
      </form>

      {!q && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb size={14} />
              Sugestões
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map((ex) => (
              <button
                key={ex}
                onClick={() => {
                  setDraft(ex);
                  router.push(`/search?q=${encodeURIComponent(ex)}`);
                }}
                className="rounded-full border border-ink-700 px-3 py-1 text-xs text-ink-200 hover:border-brand-500/50 hover:text-brand-200"
              >
                {ex}
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      {q && (
        <>
          <div className="text-xs text-ink-400">
            {res.isLoading
              ? "Calculando similaridade…"
              : `${res.data?.length ?? 0} resultados para “${q}”`}
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {res.isLoading &&
              Array.from({ length: 6 }).map((_, i) => <OpportunityCardSkeleton key={i} />)}
            {res.data?.map(({ opportunity, score, shared_keywords }) => (
              <div key={opportunity.id} className="flex flex-col gap-1">
                <div className="flex items-center justify-between gap-3 px-1">
                  <span className="text-[11px] uppercase tracking-widest text-ink-400">
                    Similaridade TF-IDF
                  </span>
                  <Badge tone="brand" className="font-mono">
                    sim {score.toFixed(2)}
                  </Badge>
                </div>
                <OpportunityCard opp={opportunity} />
                {shared_keywords.length > 0 && (
                  <div className="mt-1 flex flex-wrap items-center gap-1 px-1 text-[11px] text-ink-400">
                    <span>Palavras em comum:</span>
                    {shared_keywords.slice(0, 6).map((k) => (
                      <span
                        key={k}
                        className="rounded bg-ink-800/70 px-1.5 py-0.5 text-ink-200"
                      >
                        {k}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          {!res.isLoading && res.data?.length === 0 && (
            <EmptyState
              icon={<SearchIcon />}
              title="Nada encontrado"
              description="Tente outros termos ou remova sinônimos restritivos."
            />
          )}
        </>
      )}
    </div>
  );
}
