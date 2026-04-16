"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Input, Select } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { BRAZILIAN_STATES } from "@/lib/states";
import { FormEvent } from "react";

const SORT_OPTIONS = [
  { value: "published_at_desc", label: "Mais recentes" },
  { value: "published_at_asc", label: "Mais antigas" },
  { value: "value_desc", label: "Maior valor" },
  { value: "value_asc", label: "Menor valor" },
  { value: "closes_at_asc", label: "Fecham em breve" },
];

export function OpportunityFilters({
  modalities,
  statuses,
  categories,
}: {
  modalities: { value: string; label: string; count?: number }[];
  statuses: { value: string; label: string; count?: number }[];
  categories: { value: string; label: string; count?: number }[];
}) {
  const router = useRouter();
  const sp = useSearchParams();

  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const params = new URLSearchParams();
    for (const [k, v] of form.entries()) {
      if (typeof v === "string" && v.trim()) params.set(k, v.toString());
    }
    router.push(`/opportunities?${params.toString()}`);
  }

  function clearAll() {
    router.push("/opportunities");
  }

  return (
    <form
      onSubmit={submit}
      className="card-surface grid grid-cols-1 gap-3 rounded-xl p-4 shadow-card sm:grid-cols-2 lg:grid-cols-5"
    >
      <div className="lg:col-span-2">
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Busca
        </label>
        <Input name="q" defaultValue={sp.get("q") ?? ""} placeholder="palavra-chave" />
      </div>
      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Estado
        </label>
        <Select name="state" defaultValue={sp.get("state") ?? ""}>
          <option value="">Todos</option>
          {BRAZILIAN_STATES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </Select>
      </div>
      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Modalidade
        </label>
        <Select name="modality" defaultValue={sp.get("modality") ?? ""}>
          <option value="">Todas</option>
          {modalities.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label} {m.count !== undefined ? `· ${m.count}` : ""}
            </option>
          ))}
        </Select>
      </div>
      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Situação
        </label>
        <Select name="status" defaultValue={sp.get("status") ?? ""}>
          <option value="">Todas</option>
          {statuses.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label} {m.count !== undefined ? `· ${m.count}` : ""}
            </option>
          ))}
        </Select>
      </div>

      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Categoria
        </label>
        <Select name="category" defaultValue={sp.get("category") ?? ""}>
          <option value="">Todas</option>
          {categories.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </Select>
      </div>
      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Valor mínimo (R$)
        </label>
        <Input name="min_value" type="number" defaultValue={sp.get("min_value") ?? ""} />
      </div>
      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Valor máximo (R$)
        </label>
        <Input name="max_value" type="number" defaultValue={sp.get("max_value") ?? ""} />
      </div>
      <div>
        <label className="mb-1 block text-[11px] uppercase tracking-widest text-ink-400">
          Ordenar por
        </label>
        <Select name="sort" defaultValue={sp.get("sort") ?? "published_at_desc"}>
          {SORT_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
      </div>
      <div className="flex items-end gap-2 sm:col-span-2 lg:col-span-5 lg:justify-end">
        <Button type="button" variant="outline" onClick={clearAll}>
          Limpar
        </Button>
        <Button type="submit">Aplicar filtros</Button>
      </div>
    </form>
  );
}
