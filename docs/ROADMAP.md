# Roadmap

LicitScope is positioned as a **portfolio-grade MVP+** rather than a
production SaaS. The items below are deliberately descoped so the demo is
solid and opinionated, but each one has a clear growth path.

## Intentionally not built (yet)

| Area | Why deferred | Next step |
| --- | --- | --- |
| AuthN/Z (OIDC + RBAC) | Out of scope for a portfolio demo | Wrap FastAPI with Authlib + per-user watchlists |
| Email / webhook alerts | The MVP stores alerts server-side only | Add a `dispatch_alerts` worker + SMTP/webhook fanout |
| pgvector semantic search | TF-IDF is enough at demo scale | Migrate `fingerprint` JSON column to `vector(256)` |
| Worker queue | Single-process demo is simpler | Promote `IngestionService` into a Celery task |
| LLM-backed summarization | Would require external API keys | Implement the `Provider` protocol with Anthropic/OpenAI |
| Advanced geo viz | Choropleth needs topo data | Drop in `react-simple-maps` with IBGE shapefiles |
| Full historical backfill | Live backfill is slow + rate-limited | Nightly incremental + monthly backfill strategy |
| Multi-tenant deployment | Not a priority at demo stage | Add org-scoped filters + background workers per tenant |

## Next 90 days (if this became a real product)

- [ ] **Week 1-2** — Production-hardened ingestion: retries with circuit
      breaker, dead-letter table, per-source latency SLOs
- [ ] **Week 3-4** — Alerting MVP: SMTP + Slack + Discord webhooks with
      dedup windows and digest mode
- [ ] **Week 5-6** — AuthN with Keycloak / Supabase + user-scoped watchlists
- [ ] **Week 7-8** — pgvector migration + embedding-backed semantic search
      (keeping offline path for CI)
- [ ] **Week 9-10** — Supplier matchmaking: cross CNAE, region, and
      historical performance
- [ ] **Week 11-12** — Public read-only API tier (rate-limited) + CSV /
      Parquet exports

## Rejected ideas (for now)

- Realtime streaming (SSE / WebSockets) — PNCP publishes in discrete batches;
  realtime is lipstick.
- A separate "classifier microservice" — the taxonomy is a keyword map;
  putting it behind gRPC is over-engineering.
- A full blown DAG (Airflow / Dagster) — `run_ingestion` + `run_enrichment`
  as cron jobs covers > 95% of the value with 1% of the complexity.

## How to contribute to the roadmap

Open an issue using the `feature_request` template. Discussions land in the
issue; once consensus is reached we move it to a project board column.
