# Interview talking points

Short, sharp narratives to use when presenting LicitScope.

## 30-second pitch

> LicitScope is an open-source procurement intelligence platform for
> Brazilian public data. It ingests live notices from the PNCP API,
> normalizes them into a typed domain, enriches every record with
> **explainable, rule-based signals** — summary, keywords,
> complexity / effort / risk, price anomaly, semantic similarity — and
> exposes the result through a polished Next.js dashboard on top of a
> typed FastAPI backend. The whole stack runs on `docker compose up`,
> stays functional offline, and is covered by 71 backend tests plus a
> CI pipeline with lint, format check, typecheck, build, CodeQL, and
> a fixture-drift guard.

## Why this project is portfolio-grade

- **End-to-end.** Ingestion → normalization → enrichment → API → UI →
  watchlists, all in one coherent repo.
- **Real source integration.** The PNCP client hits
  `pncp.gov.br/api/consulta` with pagination, exponential backoff, and
  content-hash deduplication.
- **Graceful degradation.** If the live API is flaky, the same pipeline
  falls back to bundled fixtures and marks the run as `partial` with the
  reason recorded. The UI never goes blank.
- **Typed everywhere.** SQLModel at the DB, Pydantic v2 at the API,
  TypeScript at the UI. Shapes match.
- **Explainable signals.** Every score is produced by code a reviewer
  can read, and every rule that fires emits a short reason that's
  persisted and rendered in the UI. Auditability by construction.
- **Operability.** Ingestion-run bookkeeping, a source-health page,
  a raw-payload replay log keyed by SHA-256, a fixture-drift CI guard.
  Procurement is a trust surface — we act like it.

## Hard architecture trade-offs (and why)

1. **Single-process ingestion.**
   Ingestion is a service class, not a separate binary. That keeps the
   demo path tiny. At scale the same class drops into a Celery task
   without rewriting it.
2. **Hashed TF-IDF over dense embeddings.**
   Avoiding an embeddings service keeps the portfolio reproducible and
   free. The fingerprint column is JSON today and a drop-in migration
   target for `vector(1024)` when volume justifies pgvector.
3. **Rule-based enrichment as a first-class citizen.**
   Risk scoring, taxonomy, and anomaly flags live in Python files you
   can diff. Boring, and correct. Rationale is persisted so the UI can
   answer "why did this notice score 0.85 on risk?" without hand-waving.
4. **Denormalized `state` / `city` on opportunities.**
   Faceted filters need sub-ms response; joining through `agencies`
   every request is wasteful when state never changes per notice.
5. **SQLite + Postgres parity.**
   Every migration is portable. `make test` runs against SQLite in CI,
   Postgres in `make up`. This pays back tenfold when onboarding.
6. **MD5-based TF-IDF bucketing.**
   Python's `hash()` is per-process salted; using it would silently
   invalidate every stored fingerprint after a restart. There's a
   subprocess-level test that guards against reintroducing the bug.
7. **IQR-based price anomaly.**
   Standard deviation is dominated by outliers in procurement data;
   IQR / median is robust. The same heuristic flags both the per-notice
   `price_anomaly_score` and the per-CATMAT "dispersão alta" badge, so
   the two surfaces agree.
8. **Facets exclude their own dimension.**
   A user picking `modality=pregao_eletronico` still wants to see the
   counts for dispensa, concorrência, etc. — otherwise the facet is a
   tautology. The repo's `_apply_filters` takes an explicit `skip` set.

## Questions I'd expect — and how I'd answer

**Q: How does the similarity ranker scale?**
A: We load all ~N fingerprints per request into an in-process index. Fine
through ~10k rows (<50ms). Past that, migrate the JSON fingerprint column
to `vector(1024)` and replace the Python loop with pgvector's
`ORDER BY fingerprint <-> :q`. The contract doesn't change.

**Q: What happens when PNCP changes its payload shape?**
A: We persist every raw payload keyed by a SHA-256 content hash. If a
parser regression slips through, we can fix the parser and replay from
`raw_payloads` without hitting the live API. The parser is also the
single source of truth for mapping — one module, one place to look.

**Q: Why not use an LLM everywhere?**
A: Two reasons. Determinism — the demo must be reproducible offline and
in CI. Auditability — risk signals in public procurement need rules a
reviewer can critique. The `Provider` protocol means an LLM can be
plugged in for summarization without touching any call site.

**Q: Tests?**
A: 71 tests covering parsing, normalization, scoring, pricing service,
filter validation, repo upserts, semantic search, watchlists CRUD, and
mocked live-ingestion. CI runs ruff + ruff-format + pytest + Next
typecheck + Next build + fixture-drift check on every PR, plus weekly
CodeQL.

**Q: How would you productize this?**
A: `docs/ROADMAP.md` has a concrete 90-day plan — production ingestion
with circuit breakers, SMTP + webhook alert dispatch, OIDC auth,
pgvector-backed search, supplier matchmaking, CSV/Parquet exports.

## Questions to ask back

- How do you balance boring-but-auditable heuristics against black-box
  ML for high-stakes public-sector decisions?
- Where on the "every feature needs auth" spectrum are you comfortable
  shipping an internal tool?
- How do you think about demo scope vs. production scope when hiring
  for a builder profile?
