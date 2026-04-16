/**
 * Shared TypeScript types that mirror the API's response shape.
 * Kept deliberately narrow — we only type what the frontend renders.
 */

export interface AgencyRef {
  id: number;
  cnpj: string;
  name: string;
  short_name?: string | null;
  state?: string | null;
  city?: string | null;
  sphere?: string | null;
}

export interface OpportunitySummary {
  id: number;
  source: string;
  source_id: string;
  pncp_control_number?: string | null;
  title: string;
  modality: string;
  status: string;
  category?: string | null;
  estimated_value?: number | null;
  currency: string;
  state?: string | null;
  city?: string | null;
  published_at?: string | null;
  proposals_close_at?: string | null;
  agency?: AgencyRef | null;
  complexity_score?: number | null;
  risk_score?: number | null;
}

export interface OpportunityItem {
  id: number;
  lot_number?: number | null;
  item_number?: number | null;
  description: string;
  unit?: string | null;
  quantity?: number | null;
  unit_reference_price?: number | null;
  total_reference_price?: number | null;
  catmat_code?: string | null;
  catser_code?: string | null;
}

export interface Enrichment {
  summary?: string | null;
  bullet_points?: string[] | null;
  keywords?: string[] | null;
  categories?: string[] | null;
  entities?: Record<string, unknown> | null;
  important_dates?: Record<string, unknown> | null;
  complexity_score?: number | null;
  effort_score?: number | null;
  risk_score?: number | null;
  price_anomaly_score?: number | null;
  provider?: string;
  model?: string | null;
  generated_at?: string | null;
}

export interface OpportunityDetail extends OpportunitySummary {
  object_description: string;
  subcategory?: string | null;
  notice_number?: string | null;
  source_url?: string | null;
  proposals_open_at?: string | null;
  session_at?: string | null;
  awarded_at?: string | null;
  items: OpportunityItem[];
  enrichment?: Enrichment | null;
  raw_metadata?: Record<string, unknown> | null;
}

export interface SimilarOpportunity {
  opportunity: OpportunitySummary;
  score: number;
  shared_keywords: string[];
}

export interface Facet {
  value: string;
  label: string;
  count: number;
}

export interface OpportunityFacets {
  modalities: Facet[];
  statuses: Facet[];
  categories: Facet[];
  states: Facet[];
  sources: Facet[];
}

export interface PageMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface Page<T> {
  items: T[];
  meta: PageMeta;
}

export interface KPI {
  label: string;
  value: number;
  trend?: number | null;
  suffix?: string | null;
  description?: string | null;
}

export interface TimeSeriesPoint {
  date: string;
  count: number;
  value: number;
}

export interface CategoryBreakdown {
  category: string;
  count: number;
  total_value: number;
}

export interface GeoBreakdown {
  state: string;
  count: number;
  total_value: number;
}

export interface DashboardOverview {
  kpis: KPI[];
  recent: OpportunitySummary[];
  published_per_day: TimeSeriesPoint[];
  by_category: CategoryBreakdown[];
  by_state: GeoBreakdown[];
  by_modality: CategoryBreakdown[];
  top_agencies: Array<{
    agency_id: number | null;
    name: string;
    state: string | null;
    count: number;
    total_value: number;
  }>;
  source_health: Array<{
    id: number;
    source: string;
    status: string;
    started_at: string | null;
    finished_at: string | null;
    fetched: number;
    created: number;
    updated: number;
  }>;
}

export interface Agency {
  id: number;
  cnpj: string;
  name: string;
  short_name?: string | null;
  sphere?: string | null;
  branch?: string | null;
  state?: string | null;
  city?: string | null;
  ibge_code?: string | null;
  website?: string | null;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface AgencyProfile extends Agency {
  opportunity_count: number;
  contract_count: number;
  total_contracted_value: number;
  active_opportunities: number;
  top_categories: { category: string; count: number }[];
}

export interface Supplier {
  id: number;
  tax_id: string;
  tax_id_type: string;
  name: string;
  trade_name?: string | null;
  state?: string | null;
  city?: string | null;
  size?: string | null;
  main_cnae?: string | null;
}

export interface SupplierProfile extends Supplier {
  contract_count: number;
  total_contracted_value: number;
  top_agencies: { agency_id: number; count: number }[];
  top_categories: { category: string; count: number }[];
}

export interface Contract {
  id: number;
  source: string;
  source_id: string;
  pncp_control_number?: string | null;
  contract_number?: string | null;
  object_description: string;
  signed_at?: string | null;
  start_at?: string | null;
  end_at?: string | null;
  total_value?: number | null;
  currency: string;
  status: string;
  agency?: Agency | null;
  supplier?: Supplier | null;
}

export interface PricingIntelligence {
  catmat_or_catser: string;
  description_sample: string;
  observations: number;
  median_unit_price: number;
  p25_unit_price: number;
  p75_unit_price: number;
  min_unit_price: number;
  max_unit_price: number;
  anomaly_flag: boolean;
}

export interface SourceHealth {
  sources: Array<{
    source: string;
    last_success: string | null;
    runs: Array<{
      id: number;
      status: string;
      started_at: string | null;
      finished_at: string | null;
      fetched: number;
      created: number;
      updated: number;
      failed: number;
      notes?: string | null;
    }>;
  }>;
}

export interface Watchlist {
  id: number;
  name: string;
  description?: string | null;
  filters: Record<string, unknown>;
  notify_email?: string | null;
  notify_webhook_url?: string | null;
  active: boolean;
  created_at: string;
  last_run_at: string | null;
  match_count: number;
}
