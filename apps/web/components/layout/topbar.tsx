"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { FormEvent, useState } from "react";

export function Topbar() {
  const [q, setQ] = useState("");
  const router = useRouter();

  function submit(e: FormEvent) {
    e.preventDefault();
    if (q.trim().length < 2) return;
    router.push(`/search?q=${encodeURIComponent(q.trim())}`);
  }

  return (
    <header className="sticky top-0 z-20 border-b border-ink-800 bg-ink-900/85 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-[1440px] items-center gap-4 px-6">
        <Link href="/" className="text-[13px] font-semibold tracking-tight text-ink-50 lg:hidden">
          LicitScope
        </Link>
        <form onSubmit={submit} className="relative ml-auto flex-1 max-w-xl">
          <Search
            size={14}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-400"
          />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Busca semântica: ex. 'medicamentos uti', 'notebooks corporativos'…"
            className="h-9 w-full rounded-md bg-ink-800/70 pl-9 pr-3 text-sm text-ink-100 ring-1 ring-ink-700 placeholder:text-ink-400 focus:outline-none focus:ring-brand-500"
          />
        </form>
        <Link
          href="/opportunities"
          className="hidden rounded-md bg-brand-600/20 px-3 py-1.5 text-xs font-medium text-brand-200 ring-1 ring-brand-600/40 hover:bg-brand-600/30 md:inline"
        >
          Explorar licitações
        </Link>
      </div>
    </header>
  );
}
