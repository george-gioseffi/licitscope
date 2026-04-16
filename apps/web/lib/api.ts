/**
 * Typed API client. In development we go through the Next rewrite at
 * ``/proxy/*`` so the browser never needs CORS; the rewrite target is
 * controlled by ``NEXT_PUBLIC_API_BASE_URL``.
 */

import type {
  Agency,
  AgencyProfile,
  Contract,
  DashboardOverview,
  OpportunityDetail,
  OpportunityFacets,
  OpportunitySummary,
  Page,
  PricingIntelligence,
  SimilarOpportunity,
  SourceHealth,
  Supplier,
  SupplierProfile,
  Watchlist,
} from "./types";

const BASE = "/proxy";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${res.status} ${path} :: ${text.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

export interface OpportunityQuery {
  q?: string;
  state?: string;
  city?: string;
  agency_id?: number;
  modality?: string;
  status?: string;
  category?: string;
  source?: string;
  min_value?: number;
  max_value?: number;
  published_from?: string;
  published_to?: string;
  closes_from?: string;
  closes_to?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}

function toQS(q: Record<string, unknown> = {}): string {
  const params = new URLSearchParams();
  Object.entries(q).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") params.set(k, String(v));
  });
  const s = params.toString();
  return s ? `?${s}` : "";
}

export const api = {
  // --- opportunities -----------------------------------------------------
  opportunities: (q: OpportunityQuery = {}) =>
    request<Page<OpportunitySummary>>(`/opportunities${toQS(q as Record<string, unknown>)}`),
  opportunityFacets: (q: OpportunityQuery = {}) =>
    request<OpportunityFacets>(`/opportunities/facets${toQS(q as Record<string, unknown>)}`),
  opportunity: (id: number) => request<OpportunityDetail>(`/opportunities/${id}`),
  similar: (id: number, k = 5) =>
    request<SimilarOpportunity[]>(`/opportunities/${id}/similar?k=${k}`),

  // --- search ------------------------------------------------------------
  search: (q: string, k = 20) =>
    request<SimilarOpportunity[]>(`/search?q=${encodeURIComponent(q)}&k=${k}`),

  // --- meta --------------------------------------------------------------
  modalities: () => request<{ value: string; label: string }[]>(`/meta/modalities`),
  statuses: () => request<{ value: string; label: string }[]>(`/meta/statuses`),
  sources: () => request<{ value: string; label: string }[]>(`/meta/sources`),

  // --- analytics ---------------------------------------------------------
  overview: () => request<DashboardOverview>(`/analytics/overview`),

  // --- agencies ----------------------------------------------------------
  agencies: (q: { q?: string; state?: string; page?: number; page_size?: number } = {}) =>
    request<Page<Agency>>(`/agencies${toQS(q)}`),
  agency: (id: number) => request<AgencyProfile>(`/agencies/${id}`),

  // --- suppliers ---------------------------------------------------------
  suppliers: (q: { q?: string; state?: string; page?: number; page_size?: number } = {}) =>
    request<Page<Supplier>>(`/suppliers${toQS(q)}`),
  supplier: (id: number) => request<SupplierProfile>(`/suppliers/${id}`),

  // --- contracts + pricing -----------------------------------------------
  contracts: (q: Record<string, unknown> = {}) => request<Page<Contract>>(`/contracts${toQS(q)}`),
  pricing: () => request<PricingIntelligence[]>(`/contracts/pricing`),

  // --- source health -----------------------------------------------------
  sourcesHealth: () => request<SourceHealth>(`/health/sources`),

  // --- watchlists --------------------------------------------------------
  watchlists: () => request<Watchlist[]>(`/watchlists`),
  createWatchlist: (body: unknown) =>
    request<Watchlist>(`/watchlists`, { method: "POST", body: JSON.stringify(body) }),
  deleteWatchlist: (id: number) => request<void>(`/watchlists/${id}`, { method: "DELETE" }),
  runWatchlist: (id: number) =>
    request<OpportunitySummary[]>(`/watchlists/${id}/run`, { method: "POST" }),
};
