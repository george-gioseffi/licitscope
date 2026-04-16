# LicitScope API

FastAPI backend for **LicitScope**, an AI-powered procurement intelligence
platform focused on Brazilian public procurement data (PNCP, Portal da
Transparência, Compras.gov.br).

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
