# Local development

## Option 1 — Docker Compose (simplest)

```bash
cp .env.example .env
make up                         # postgres + api + web
```

- API: http://localhost:8000 (docs at `/docs`)
- Web: http://localhost:3000

The first run auto-seeds demo fixtures. To reset:

```bash
make reset-db
make up
```

## Option 2 — Local Python + Node, SQLite

```bash
./scripts/dev-setup.sh          # venv, install, seed SQLite DB
make api &                      # uvicorn with reload
make web                        # next dev
```

Useful Make targets:

| Target | What it does |
| --- | --- |
| `make install`   | Install backend (editable) + frontend deps |
| `make seed`      | Reload the fixtures into the configured DB |
| `make ingest`    | Run one ingestion pass (live PNCP by default) |
| `make enrich`    | Re-run enrichment over all notices |
| `make test`      | Backend pytest |
| `make lint`      | ruff + next lint |
| `make typecheck` | tsc --noEmit |

## Environment variables

| Var | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./licitscope.db` | Any SQLAlchemy URL |
| `INGESTION_USE_FIXTURES` | `true` | If false, hit live PNCP |
| `PNCP_BASE_URL` | `https://pncp.gov.br/api/consulta` | Override for mocks |
| `INGESTION_PAGE_SIZE` | `50` | Page size for PNCP pagination |
| `INGESTION_MAX_PAGES` | `5` | Hard bound per modality per run |
| `ENRICHMENT_MODE` | `offline` | `offline` or `llm` |
| `LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` | empty | Enable LLM enrichment |
| `API_CORS_ORIGINS` | `http://localhost:3000` | Comma-separated |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Web → API base |

## Useful commands during development

```bash
# Inspect API schema
curl -s http://localhost:8000/openapi.json | jq '.paths | keys'

# Hit a single opportunity
curl -s http://localhost:8000/opportunities?page_size=1 | jq

# Re-seed if the fixtures change
cd apps/api && python -m app.scripts.seed

# Run a specific test file
cd apps/api && pytest tests/test_api.py -v

# Regenerate demo fixtures deterministically
python scripts/generate_fixtures.py
```

## Troubleshooting

### "SQLite DateTime type only accepts Python datetime" during seed

You likely seeded with fixtures that contained ISO-string dates. The seeder
coerces them automatically; confirm you're running the latest
`app/scripts/seed.py`.

### Next build complains about `useSearchParams` without Suspense

This was fixed in `app/opportunities/page.tsx` and `app/search/page.tsx`
by wrapping the inner page in `<Suspense>`. If you add a new client page
that reads the query string, follow the same pattern.

### CORS blocks the frontend

Set `API_CORS_ORIGINS` to your web origin, or use the built-in Next.js
rewrite at `/proxy/*` (which is what the app does by default).
