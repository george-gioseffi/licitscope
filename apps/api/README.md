# LicitScope API

FastAPI backend for **LicitScope**, an explainable procurement
intelligence platform focused on Brazilian public procurement data.
The backend ingests live PNCP notices, normalizes them into a typed
domain, enriches every record with rule-based signals (summary,
keywords, scoring, price anomaly) and exposes a typed REST surface at
`/docs`. Portal da Transparência and Compras.gov.br are on the
[roadmap](../../docs/ROADMAP.md).

See the [top-level README](../../README.md) for the architecture overview,
the [docs folder](../../docs) for data model, ingestion, and enrichment
notes, and [`pyproject.toml`](./pyproject.toml) for dependencies.

## Quick start (local, SQLite)

```bash
python -m venv .venv
. .venv/Scripts/activate          # Windows; use source .venv/bin/activate on *nix
pip install -e ".[dev]"
DATABASE_URL=sqlite:///./licitscope.db python -m app.scripts.seed
DATABASE_URL=sqlite:///./licitscope.db uvicorn app.main:app --reload
```

Open <http://localhost:8000/docs> for the interactive OpenAPI explorer.
