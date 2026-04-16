"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Bell,
  Building2,
  Database,
  FileText,
  Gauge,
  Home,
  Info,
  Search,
  Telescope,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_PRIMARY = [
  { label: "Visão geral", href: "/", icon: Home },
  { label: "Licitações", href: "/opportunities", icon: FileText },
  { label: "Busca semântica", href: "/search", icon: Search },
  { label: "Contratos & preços", href: "/contracts", icon: BarChart3 },
];

const NAV_ENTITIES = [
  { label: "Órgãos", href: "/agencies", icon: Building2 },
  { label: "Fornecedores", href: "/suppliers", icon: Users },
];

const NAV_OPS = [
  { label: "Watchlists", href: "/watchlists", icon: Bell },
  { label: "Saúde das fontes", href: "/health", icon: Activity },
  { label: "Sobre", href: "/about", icon: Info },
];

function NavGroup({
  label,
  items,
  pathname,
}: {
  label: string;
  items: typeof NAV_PRIMARY;
  pathname: string;
}) {
  return (
    <div>
      <div className="mb-1 mt-5 px-3 text-[10px] font-semibold uppercase tracking-widest text-ink-500">
        {label}
      </div>
      <div className="flex flex-col gap-0.5">
        {items.map(({ label, href, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-[13px] transition",
                active
                  ? "bg-brand-600/15 text-ink-50 ring-1 ring-brand-500/40"
                  : "text-ink-300 hover:bg-ink-800 hover:text-ink-100",
              )}
            >
              <Icon size={16} />
              <span>{label}</span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-ink-800 bg-ink-900/80 p-4 backdrop-blur lg:flex">
      <div className="flex items-center gap-2 px-2 py-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-violet-500 shadow-glow">
          <Telescope size={18} className="text-white" />
        </div>
        <div>
          <div className="text-[13px] font-semibold tracking-tight text-ink-50">LicitScope</div>
          <div className="text-[10px] uppercase tracking-widest text-ink-400">
            Procurement Intelligence
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto">
        <NavGroup label="Descobrir" items={NAV_PRIMARY} pathname={pathname} />
        <NavGroup label="Entidades" items={NAV_ENTITIES} pathname={pathname} />
        <NavGroup label="Operação" items={NAV_OPS} pathname={pathname} />
      </nav>

      <div className="mt-4 rounded-xl border border-ink-800 bg-ink-900/60 p-3 text-[11px] text-ink-400">
        <div className="mb-1 flex items-center gap-1 text-ink-200">
          <Gauge size={12} /> <span className="font-medium">Enriquecimento offline</span>
        </div>
        Resumos, extração e similaridade são gerados por regras determinísticas — sem
        chamadas a LLMs externos por padrão.
      </div>
      <div className="mt-3 flex items-center gap-2 px-2 text-[11px] text-ink-500">
        <Database size={12} /> Fonte primária: PNCP
      </div>
    </aside>
  );
}
