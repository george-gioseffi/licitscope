"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, Plus, Trash2, Play } from "lucide-react";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input, Select } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { BRAZILIAN_STATES } from "@/lib/states";

export default function WatchlistsPage() {
  const qc = useQueryClient();
  const list = useQuery({ queryKey: ["watchlists"], queryFn: api.watchlists });

  const [name, setName] = useState("");
  const [q, setQ] = useState("");
  const [state, setState] = useState("");
  const [modality, setModality] = useState("");

  const create = useMutation({
    mutationFn: api.createWatchlist,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["watchlists"] });
      setName(""); setQ(""); setState(""); setModality("");
    },
  });

  const del = useMutation({
    mutationFn: api.deleteWatchlist,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
  });

  const run = useMutation({
    mutationFn: api.runWatchlist,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["watchlists"] }),
  });

  function submit(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    create.mutate({
      name,
      filters: { q: q || null, state: state || null, modality: modality || null, sort: "published_at_desc" },
    });
  }

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Watchlists"
        title="Monitore licitações sob medida"
        description="Salve filtros e receba alertas quando novas licitações compatíveis forem publicadas. No MVP, os alertas ficam armazenados localmente no backend e podem ser executados manualmente ou agendados."
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus size={14} /> Criar nova watchlist
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={submit}
            className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5"
          >
            <div className="lg:col-span-2">
              <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">Nome</label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="ex: TI SP" />
            </div>
            <div>
              <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">Palavra-chave</label>
              <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="ex: software" />
            </div>
            <div>
              <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">Estado</label>
              <Select value={state} onChange={(e) => setState(e.target.value)}>
                <option value="">Todos</option>
                {BRAZILIAN_STATES.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </Select>
            </div>
            <div>
              <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">Modalidade</label>
              <Select value={modality} onChange={(e) => setModality(e.target.value)}>
                <option value="">Todas</option>
                <option value="pregao_eletronico">Pregão eletrônico</option>
                <option value="dispensa">Dispensa</option>
                <option value="concorrencia">Concorrência</option>
                <option value="credenciamento">Credenciamento</option>
              </Select>
            </div>
            <div className="flex items-end sm:col-span-2 lg:col-span-5 lg:justify-end">
              <Button type="submit" disabled={create.isPending}>
                <Plus size={14} />
                Salvar watchlist
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {list.data?.length === 0 && (
          <EmptyState
            icon={<Bell />}
            title="Sem watchlists ainda"
            description="Crie uma combinação de filtros acima para começar a monitorar."
          />
        )}
        {list.data?.map((w) => (
          <Card key={w.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>{w.name}</CardTitle>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => run.mutate(w.id)}
                    className="rounded-md bg-brand-600/15 px-2.5 py-1 text-[11px] font-medium text-brand-200 ring-1 ring-brand-600/40 hover:bg-brand-600/25"
                  >
                    <span className="inline-flex items-center gap-1"><Play size={10}/> Executar</span>
                  </button>
                  <button
                    onClick={() => del.mutate(w.id)}
                    className="rounded-md bg-rose-600/10 px-2.5 py-1 text-[11px] font-medium text-rose-200 ring-1 ring-rose-500/30 hover:bg-rose-600/20"
                  >
                    <span className="inline-flex items-center gap-1"><Trash2 size={10}/> Remover</span>
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-ink-400">
                {w.match_count} alertas · criado em {new Date(w.created_at).toLocaleDateString("pt-BR")}
              </div>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {Object.entries(w.filters).map(([k, v]) =>
                  v ? (
                    <Badge key={k} tone="outline">
                      {k}: {String(v)}
                    </Badge>
                  ) : null,
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
