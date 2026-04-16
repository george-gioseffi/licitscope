# Release readiness notes

Short checklist for cutting a tagged release of LicitScope.

## Before you tag

1. **All green**: `make test` · `make lint` · `make typecheck` ·
   `cd apps/web && npm run build`.
2. **Fixtures byte-stable**: `python scripts/generate_fixtures.py`
   followed by `git diff --exit-code data-demo` — must be clean.
3. **OpenAPI snapshot** is current:

   ```bash
   cd apps/api
   .venv/Scripts/python - <<'PY'
   import json
   from app.main import app
   print(json.dumps(app.openapi(), indent=2))
   PY
   ```

   Commit the diff to `docs/openapi.json` if you keep one.
4. **Screenshots** captured per [`docs/SCREENSHOTS.md`](SCREENSHOTS.md).
5. **CHANGELOG** updated — move entries from `## [Unreleased]` to a new
   version section with today's date.
6. **README badges** still resolve (GH Actions CI badge is correct once
   the workflow has run at least once on main).

## Repo metadata (GitHub)

- **Description**: `Explainable procurement intelligence for Brazilian
  public data — PNCP ingestion, rule-based enrichment, TF-IDF search,
  and pricing anomaly signals. FastAPI + Next.js, Docker, CI-covered.`
- **Topics**: `govtech` `procurement` `brazil` `pncp` `fastapi`
  `nextjs` `sqlmodel` `tailwindcss` `data-engineering` `open-data`
  `tf-idf` `portfolio-project` `typescript` `python`
- **Homepage**: leave empty or set to the Vercel deploy once the
  frontend is hosted.
- **Social preview**: `docs/assets/logo.svg` (render to PNG 1280×640 if
  GitHub requires bitmap).

## Suggested release message

```
v0.1.0 — first release

LicitScope v0.1.0 is the first public cut: a working PNCP ingestion
pipeline, explainable rule-based enrichment, hashed TF-IDF semantic
search, IQR-based price anomaly signals, a polished Next.js dashboard,
and 71 passing tests on CI. See CHANGELOG for the full list.
```

## Post-release

- Verify CI passes on main after the merge.
- Update `docs/ROADMAP.md` — move shipped items out of "Next 90 days".
- Open follow-up issues for any TODO that didn't make the cut.
