# Demo screenshots to capture

For a portfolio walk-through, capture these screens in order. They tell a
story from "here's the product" to "here's the technical depth".

> ⚙️  Command to seed the recommended demo state:
> ```bash
> make up           # docker compose stack
> # or locally:
> DATABASE_URL=sqlite:///./licitscope.db python -m app.scripts.seed
> ```

## 1. Overview dashboard — `/`

- KPI row showing notices, total value, open proposals, average risk
- 30-day publication timeline
- Modality donut
- Top categories (horizontal bar)
- Geographic distribution (vertical bar)
- Top agencies list
- Source-health tile

**Why**: shows data density and UX polish in a single screen.

## 2. Opportunities feed — `/opportunities`

- Filter bar expanded (state = SP, modality = pregão eletrônico)
- A dozen opportunity cards with modality + status badges
- Sort dropdown showing "Maior valor"

**Why**: demonstrates the faceted filtering + facet-count UX.

## 3. Opportunity detail — `/opportunities/{id}`

- Enrichment card showing AI summary + bullets + keywords
- Heuristic signals (complexity, effort, risk bars)
- Dates panel with upcoming deadline highlighted in amber
- Items table
- Similar opportunities panel (right column)

**Why**: the product's intelligence layer in a single view.

## 4. Semantic search — `/search?q=medicamentos`

- Ranked results with cosine scores as badges
- Shared-keywords chip row under each card

**Why**: shows the offline semantic search in action.

## 5. Contracts & pricing — `/contracts`

- Pricing intelligence table with P25/median/P75 and anomaly flags
- Recent-contracts list

**Why**: demonstrates pricing intelligence without needing a ton of data.

## 6. Agency profile — `/agencies/{id}`

- KPI row (licitações, ativas, contratos, valor contratado)
- Recent opportunities grid
- Top categories list

**Why**: shows that the data model supports profile pages naturally.

## 7. Watchlists — `/watchlists`

- Form to create a new watchlist
- Saved watchlists grid with match counts

**Why**: product-management-style "so what does a user do here?"

## 8. Source health — `/health`

- List of recent ingestion runs with status badges and counts

**Why**: ops maturity.

## 9. API docs — `http://localhost:8000/docs`

- The FastAPI interactive swagger — great to show typed contracts

**Why**: shows that the whole product is backed by a strongly-typed API.

## Production tips

- Use a 1440px-wide browser at 100% zoom.
- Dark mode is the default; keep it that way — it's the polished theme.
- Before capturing, trigger at least one ingestion run so the source-health
  panel is populated.
- For the opportunity detail screenshot, pick a notice with a risk score
  above 0.7 so the amber alert box appears.
