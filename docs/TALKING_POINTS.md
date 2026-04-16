# Interview talking points

Short, sharp narratives to use when presenting LicitScope.

## 30-second pitch

> LicitScope is an open-source AI procurement intelligence platform for
> Brazilian public procurement data. It ingests live data from the PNCP
> API, normalizes it into a typed domain model, enriches every notice
> with explainable AI heuristics — summary, keywords, risk, price
> dispersion — and exposes a polished Next.js dashboard over a typed
> FastAPI backend. The entire stack runs locally with
> `docker compose up` and is covered by CI with 49 backend tests.

## Why this project is portfolio-grade

- **End-to-end**: ingestion → normalization → enrichment → API → UI → alerts.
- **Real source integration**: the PNCP client actually hits
  `pncp.gov.br/api/consulta` with pagination, retry, and parsing.
- **Graceful fallback**: if the live API is flaky, the same pipeline runs
  against deterministic fixtures, so the demo never breaks.
- **Typed everywhere**: SQLModel at the DB, Pydantic v2 at the API,
  TypeScript at the UI, all with shared shapes.
- **Explainable AI**: no LLM required by default; every score is
  computed from a rule a human can critique.
- **Operability**: ingestion-run bookkeeping, a source-health page, and
  a raw-payload replay log — because in govtech, auditability matters.

## Hard architecture trade-offs I made (and why)

1. **Single-process ingestion**
   The demo path stays tiny because ingestion is a service class, not a
   separate binary. At scale the same class drops into a Celery task.
2. **Hashed TF-IDF over vectors**
   Avoiding an embedding service keeps the portfolio reproducible. The
   fingerprint column is JSON today and a migration target for pgvector.
3. **Rule-based enrichment as a first-class citizen**
   Risk scoring, taxonomy, and anomaly flags are all in Python modules
   you can diff. It's boring. That's the point — boring is auditable.
4. **Denormalized `state`/`city` on opportunities**
   Faceted filters need sub-ms response; joining through agency every time
   is wasteful and doesn't pay rent for this query pattern.
5. **SQLite + Postgres parity**
   Every migration is portable. `make test` runs against SQLite in CI and
   Postgres in `make up`. This pays dividends when onboarding collaborators.

## Questions I'd expect an interviewer to ask

**Q: How does the similarity ranker scale?**
A: In-process TF-IDF indexing loads all ~N fingerprints per request. That's
fine through ~10k rows. Past that, we migrate `fingerprint` from JSON to
`vector(256)` and replace the loop with pgvector `ORDER BY <->`.

**Q: What happens when PNCP changes its payload?**
A: We save every raw payload keyed by a SHA-256 content hash. Bugs in the
parser can be replayed against stored payloads without hitting the API
again. That decouples ingestion from normalization.

**Q: Why not use an LLM everywhere?**
A: Two reasons. First, determinism: the demo must be reproducible offline.
Second, auditability: for govtech, a risk signal needs a rule you can
critique. The `Provider` protocol means you can plug in an LLM later for
the summary without touching anything else.

**Q: Tests?**
A: 49 pytest tests covering parsing, normalization, scoring, analytics
endpoints, watchlists CRUD, and mocked live-ingestion via respx. CI runs
ruff + pytest + Next typecheck + build on every PR.

**Q: How would you productize this?**
A: The roadmap in `docs/ROADMAP.md` has a concrete 90-day plan:
production ingestion with circuit breakers, SMTP+webhook alerts, AuthN,
pgvector semantic search, supplier matchmaking, and exports.

## Questions to ask back

- How do you approach balancing boring-but-auditable heuristics vs
  black-box ML in high-stakes domains?
- Where are you on the "every feature needs auth" spectrum for new
  products?
- How do you think about scope for portfolio demos vs production systems?
