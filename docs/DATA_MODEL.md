# Data model

LicitScope's schema is intentionally small and normalized. Every SQLModel
class in `apps/api/app/models/` corresponds to one table; relationships
follow the business entities closely so the API surface maps 1:1 to the
model layer.

## Entity-relationship diagram

```mermaid
erDiagram
    AGENCY ||--o{ OPPORTUNITY : "issues"
    AGENCY ||--o{ CONTRACT    : "owns"
    OPPORTUNITY ||--o{ OPPORTUNITY_ITEM : "contains"
    OPPORTUNITY ||--|| ENRICHMENT : "enriches"
    OPPORTUNITY ||--o{ CONTRACT : "awarded to"
    SUPPLIER ||--o{ CONTRACT : "supplies"
    CONTRACT ||--o{ CONTRACT_ITEM : "contains"
    WATCHLIST ||--o{ ALERT : "fires"
    INGESTION_RUN ||--o{ RAW_PAYLOAD : "produces"

    AGENCY {
        int id PK
        string cnpj UK
        string name
        string sphere
        string state
        string city
    }

    OPPORTUNITY {
        int id PK
        string source
        string source_id
        string pncp_control_number
        string title
        string object_description
        string modality
        string status
        string category
        float  estimated_value
        datetime published_at
        datetime proposals_close_at
        string state
        string city
        int    agency_id FK
        jsonb  raw_metadata
    }

    OPPORTUNITY_ITEM {
        int id PK
        int opportunity_id FK
        string description
        string catmat_code
        string catser_code
        float  quantity
        float  unit_reference_price
    }

    ENRICHMENT {
        int id PK
        int opportunity_id FK
        text   summary
        jsonb  keywords
        jsonb  categories
        float  complexity_score
        float  effort_score
        float  risk_score
        float  price_anomaly_score
        jsonb  fingerprint
        string provider
    }

    SUPPLIER {
        int id PK
        string tax_id UK
        string name
        string state
        string main_cnae
    }

    CONTRACT {
        int id PK
        int opportunity_id FK
        int agency_id FK
        int supplier_id FK
        string contract_number
        float  total_value
        datetime signed_at
        string status
    }

    CONTRACT_ITEM {
        int id PK
        int contract_id FK
        string description
        float  unit_price
        string catmat_code
    }

    WATCHLIST {
        int id PK
        string name
        jsonb  filters
        bool   active
    }

    ALERT {
        int id PK
        int watchlist_id FK
        int opportunity_id FK
        string headline
    }

    INGESTION_RUN {
        int id PK
        string source
        string status
        int fetched
        int created
        datetime started_at
    }

    RAW_PAYLOAD {
        int id PK
        int ingestion_run_id FK
        string source
        string kind
        string content_hash
        jsonb  payload
    }
```

## Keys, indexes, and why

| Table | Keys / indexes | Reason |
| --- | --- | --- |
| `opportunities` | `UNIQUE (source, source_id)` | Canonical cross-source dedup |
| `opportunities` | index on `published_at`, `proposals_close_at`, `state`, `modality`, `status`, `category`, `agency_id`, `estimated_value` | Backs the faceted feed without scans |
| `agencies` | `UNIQUE cnpj` | Stable lookup from any payload |
| `suppliers` | `UNIQUE tax_id` | Same as above |
| `enrichments` | `UNIQUE opportunity_id` | Exactly one enrichment per notice |
| `raw_payloads` | index on `(source, kind, source_id, content_hash)` | Idempotent payload saves |

## Where the flexibility lives

Three columns deliberately stay JSON:

- `opportunities.raw_metadata` — the untouched source payload. Invaluable
  when a normalization bug slips through.
- `enrichments.fingerprint`    — sparse TF-IDF vector. JSON today; swap with
  `vector` type when enabling pgvector.
- `watchlists.filters`         — mirrors the `OpportunityFilters` Pydantic
  model so the frontend can post the same shape it renders with.

## Portability

Everything compiles against both SQLite (tests, laptop runs) and Postgres
(Docker, production). No Postgres-specific types are used in the schema.
Future pgvector adoption is confined to the fingerprint column; see the
roadmap for the planned migration.
