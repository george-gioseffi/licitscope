# Ingestion

LicitScope ingests Brazilian public procurement data from the **Portal
Nacional de Contratações Públicas (PNCP)**, which exposes a public,
unauthenticated HTTP API under `https://pncp.gov.br/api/consulta`.

## Endpoints we rely on

| Endpoint | Purpose | Notes |
| --- | --- | --- |
| `GET /v1/contratacoes/publicacao` | List notices by publication date | Requires `codigoModalidadeContratacao` and a window ≤ a few days |
| `GET /v1/contratos/publicacao`    | List contracts by publication date | Similar pagination shape |
| `GET /v1/orgaos/{cnpj}/compras/{ano}/{seq}` | Single-notice lookup | Used for enrichment |

The live PNCP API is **rate-limited** and occasionally returns 4xx errors
for wide windows. Our client (`apps/api/app/clients/pncp.py`) addresses
this with:

- `tenacity`-based exponential backoff on timeouts and transport errors
- Explicit pagination with a safety bound (`INGESTION_MAX_PAGES`)
- A hard page-size cap (`INGESTION_PAGE_SIZE`)

## Control flow

```
┌──────────────────────────────┐       ┌────────────────┐
│ IngestionService.start_run()│──────▶│ IngestionRun   │
└────────────┬─────────────────┘       └────────────────┘
             ▼
 ┌───────────────────────────┐    HTTP fallback on failure
 │ PNCPClient pages notices  │◀─────── fixtures snapshot
 └────────────┬──────────────┘
              ▼
 ┌───────────────────────────┐
 │ pncp_parser.parse_full()  │ ── parse → (agency, opportunity, items)
 └────────────┬──────────────┘
              ▼
 ┌───────────────────────────┐
 │ Repository upserts        │ ── (source, source_id) dedup
 └────────────┬──────────────┘
              ▼
 ┌───────────────────────────┐
 │ RawPayload.save_payload() │ ── idempotent by content hash
 └───────────────────────────┘
```

## Idempotency

Each `RawPayload` row is keyed by `(source, kind, source_id, content_hash)`.
The hash is `sha256(json.dumps(payload, sort_keys=True))`, so re-running
ingestion over the same window never creates duplicate rows. The
`Opportunity.source + source_id` unique constraint gives the same guarantee
at the domain level — re-runs update existing rows in place.

## Running ingestion

```bash
# one-off
INGESTION_USE_FIXTURES=false python -m app.scripts.run_ingestion

# force the fixtures path (default in the demo)
INGESTION_USE_FIXTURES=true  python -m app.scripts.run_ingestion

# schedule it (cron example)
0 */3 * * * cd /opt/licitscope && . apps/api/.venv/bin/activate && \
    python -m app.scripts.run_ingestion >> /var/log/licitscope-ingest.log 2>&1
```

## Observability

Every run writes:

- an `IngestionRun` row with status, fetched/created/updated/failed counts,
  and human-readable `notes` on partial failures
- one `RawPayload` per unique notice payload, giving a full replay log

The `/health/sources` endpoint and the `/health` page in the web app surface
this data so operators can tell at a glance whether a feed went stale.

## Graceful fallback

If the live PNCP request fails (timeout, 5xx, parser exception):

1. The `IngestionRun` is finalized with `status="partial"`.
2. `IngestionService` falls back to loading `data-demo/pncp/opportunities.json`.
3. The run's `notes` column records the reason.

This keeps demos reliable — recruiters looking at the dashboard will always
see meaningful data, even when the remote API is down.

## Extending to other sources

The cleanest seam to add a second source is:

1. Build a new client under `app/clients/{source}.py`.
2. Build a parser under `app/clients/{source}_parser.py` with the exact
   same `parse_full` signature returning `(agency, opportunity, items)`.
3. Add the source's string to `SourceName` in `app/models/enums.py`.
4. Add a method to `IngestionService` — or parameterize the existing one
   over the client — and wire it in `run_ingestion.py`.

The rest of the system is source-agnostic: the domain model uses
`(source, source_id)` everywhere.
