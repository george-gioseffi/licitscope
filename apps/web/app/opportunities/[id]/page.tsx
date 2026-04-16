"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import {
  AlertTriangle,
  Building2,
  Calendar,
  CalendarClock,
  ExternalLink,
  FileText,
  Gauge,
  MapPin,
  Sparkles,
  Tag,
} from "lucide-react";
import { api } from "@/lib/api";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  ModalityBadge,
  StatusBadge,
} from "@/components/opportunities/modality-badge";
import {
  formatBRL,
  formatCompactBRL,
  formatDate,
  formatDateTime,
  daysUntil,
} from "@/lib/utils";

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const oid = Number(id);

  const opp = useQuery({
    queryKey: ["opp", oid],
    queryFn: () => api.opportunity(oid),
    enabled: !!oid,
  });

  const similar = useQuery({
    queryKey: ["similar", oid],
    queryFn: () => api.similar(oid, 6),
    enabled: !!oid,
  });

  if (opp.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-96" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-6 w-4/5" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  if (opp.isError || !opp.data) {
    return (
      <div className="flex flex-col gap-4">
        <h1 className="text-lg font-semibold">Licitação não encontrada</h1>
        <Link href="/opportunities" className="text-brand-300 hover:underline">
          ← Voltar ao feed
        </Link>
      </div>
    );
  }

  const d = opp.data;
  const closeIn = daysUntil(d.proposals_close_at);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow={d.agency?.name ?? "Licitação"}
        title={d.title}
        description={d.object_description.slice(0, 240) + (d.object_description.length > 240 ? "…" : "")}
        actions={
          d.source_url ? (
            <a
              href={d.source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-md bg-brand-600/20 px-3 py-1.5 text-xs font-medium text-brand-200 ring-1 ring-brand-600/40 hover:bg-brand-600/30"
            >
              Abrir no portal oficial <ExternalLink size={12} />
            </a>
          ) : null
        }
      />

      {/* Badges row */}
      <div className="flex flex-wrap items-center gap-2">
        <ModalityBadge value={d.modality} />
        <StatusBadge value={d.status} />
        {d.category && <Badge tone="violet">{d.category}</Badge>}
        {d.pncp_control_number && (
          <Badge tone="outline" className="font-mono">
            PNCP {d.pncp_control_number}
          </Badge>
        )}
        {d.state && (
          <Badge tone="outline">
            <MapPin size={10} /> {d.city} / {d.state}
          </Badge>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main column */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="text-brand-300" size={14} /> Resumo enriquecido
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {d.enrichment?.summary ? (
                <p className="text-sm leading-relaxed text-ink-100">{d.enrichment.summary}</p>
              ) : (
                <p className="text-sm text-ink-400">
                  Nenhum resumo disponível — rode o enriquecimento com{" "}
                  <code className="rounded bg-ink-800 px-1 py-0.5">python -m app.scripts.run_enrichment</code>.
                </p>
              )}
              {d.enrichment?.bullet_points?.length ? (
                <ul className="space-y-1.5 text-[13px] text-ink-200">
                  {d.enrichment.bullet_points.map((b, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="mt-[7px] h-[5px] w-[5px] shrink-0 rounded-full bg-brand-400" />
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              ) : null}
              {d.enrichment?.keywords?.length ? (
                <div className="flex flex-wrap gap-1.5">
                  {d.enrichment.keywords.map((k) => (
                    <Badge tone="outline" key={k}>
                      <Tag size={10} /> {k}
                    </Badge>
                  ))}
                </div>
              ) : null}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Descrição completa do objeto</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink-100">
                {d.object_description}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText size={14} /> Itens ({d.items.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              {d.items.length === 0 ? (
                <p className="text-sm text-ink-400">Itens não disponíveis nesta fonte.</p>
              ) : (
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-left text-[10px] uppercase tracking-widest text-ink-400">
                      <th className="px-2 py-2">#</th>
                      <th className="px-2 py-2">Descrição</th>
                      <th className="px-2 py-2">Un.</th>
                      <th className="px-2 py-2 text-right">Qtd.</th>
                      <th className="px-2 py-2 text-right">Valor unit.</th>
                      <th className="px-2 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-ink-800">
                    {d.items.map((it) => (
                      <tr key={it.id} className="text-ink-200">
                        <td className="px-2 py-2 text-ink-400">{it.item_number}</td>
                        <td className="px-2 py-2">
                          <div className="font-medium text-ink-100">{it.description}</div>
                          {it.catmat_code && (
                            <div className="text-[10px] text-ink-500">CATMAT {it.catmat_code}</div>
                          )}
                        </td>
                        <td className="px-2 py-2 text-ink-300">{it.unit ?? "—"}</td>
                        <td className="px-2 py-2 text-right tabular-nums">
                          {it.quantity ?? "—"}
                        </td>
                        <td className="px-2 py-2 text-right tabular-nums">
                          {formatBRL(it.unit_reference_price ?? null)}
                        </td>
                        <td className="px-2 py-2 text-right tabular-nums">
                          {formatCompactBRL(it.total_reference_price ?? null)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Side column */}
        <div className="flex flex-col gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gauge size={14} /> Sinais heurísticos
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-3 text-[12px]">
              <SignalRow
                label="Complexidade"
                value={d.enrichment?.complexity_score}
                tone="brand"
              />
              <SignalRow label="Esforço" value={d.enrichment?.effort_score} tone="mint" />
              <SignalRow label="Risco" value={d.enrichment?.risk_score} tone="amber" />
              {d.enrichment?.price_anomaly_score != null && (
                <SignalRow
                  label="Dispersão de preços"
                  value={d.enrichment.price_anomaly_score}
                  tone="rose"
                />
              )}
              {d.enrichment?.risk_score && d.enrichment.risk_score > 0.7 && (
                <div className="mt-2 flex items-start gap-2 rounded-md border border-amber-500/30 bg-amber-500/10 p-2 text-[11px] text-amber-200">
                  <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                  <span>
                    Sinal de risco elevado — revise prazos curtos, modalidade de urgência ou termos emergenciais.
                  </span>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Datas-chave</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-[12px]">
              <DateRow icon={<Calendar size={12} />} label="Publicada" value={d.published_at} />
              <DateRow
                icon={<CalendarClock size={12} />}
                label="Abertura das propostas"
                value={d.proposals_open_at}
              />
              <DateRow
                icon={<CalendarClock size={12} />}
                label="Encerramento"
                value={d.proposals_close_at}
                highlight={closeIn !== null && closeIn <= 7}
              />
              {d.session_at && (
                <DateRow icon={<Calendar size={12} />} label="Sessão" value={d.session_at} />
              )}
              {d.awarded_at && (
                <DateRow icon={<Calendar size={12} />} label="Homologação" value={d.awarded_at} />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 size={14} /> Órgão
              </CardTitle>
            </CardHeader>
            <CardContent>
              {d.agency ? (
                <div className="text-[13px]">
                  <div className="font-medium text-ink-100">{d.agency.name}</div>
                  <div className="mt-0.5 font-mono text-[11px] text-ink-400">
                    CNPJ {d.agency.cnpj}
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1">
                    {d.agency.sphere && <Badge tone="outline">{d.agency.sphere}</Badge>}
                    {d.agency.state && <Badge tone="outline">{d.agency.state}</Badge>}
                    {d.agency.city && <Badge tone="outline">{d.agency.city}</Badge>}
                  </div>
                  <Link
                    href={`/agencies/${d.agency.id}`}
                    className="mt-3 inline-block text-xs text-brand-300 hover:underline"
                  >
                    Ver perfil do órgão →
                  </Link>
                </div>
              ) : (
                <span className="text-ink-400">Órgão não vinculado.</span>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Licitações similares</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-[12px]">
              {similar.isLoading && <Skeleton className="h-16" />}
              {!similar.isLoading && similar.data?.length === 0 && (
                <span className="text-ink-400">Nenhum vizinho encontrado.</span>
              )}
              {similar.data?.map(({ opportunity: o, score, shared_keywords }) => (
                <Link
                  key={o.id}
                  href={`/opportunities/${o.id}`}
                  className="rounded-md border border-ink-800 bg-ink-900/40 p-2 hover:border-brand-500/40"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="line-clamp-2 text-[12px] text-ink-100">{o.title}</div>
                    <Badge tone="brand" className="shrink-0 font-mono">
                      {score.toFixed(2)}
                    </Badge>
                  </div>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {shared_keywords.slice(0, 4).map((k) => (
                      <Badge key={k} tone="outline">
                        {k}
                      </Badge>
                    ))}
                  </div>
                </Link>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function SignalRow({
  label,
  value,
  tone,
}: {
  label: string;
  value: number | null | undefined;
  tone: "brand" | "amber" | "rose" | "mint";
}) {
  const v = value ?? 0;
  return (
    <div className="flex items-center gap-3">
      <span className="w-40 text-ink-300">{label}</span>
      <Progress value={v} tone={tone} label={(v * 100).toFixed(0) + "%"} />
    </div>
  );
}

function DateRow({
  icon,
  label,
  value,
  highlight,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | null | undefined;
  highlight?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center gap-1.5 text-ink-400">
        {icon}
        {label}
      </span>
      <span
        className={`tabular-nums ${
          highlight ? "text-amber-300" : "text-ink-100"
        }`}
      >
        {formatDateTime(value)}
      </span>
    </div>
  );
}
