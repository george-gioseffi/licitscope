# LicitScope docs

Short index — start with `../README.md` for the project overview, then
dive into whichever doc matches the question.

## Core

| Doc | Read this if you want to… |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Understand how the monorepo layers fit together |
| [`DATA_MODEL.md`](DATA_MODEL.md) | See the DB schema, ERD, and index choices |
| [`INGESTION.md`](INGESTION.md) | Hook up a new source or harden the PNCP path |
| [`ENRICHMENT.md`](ENRICHMENT.md) | Edit scoring rules or plug in a real LLM |
| [`LOCAL_DEV.md`](LOCAL_DEV.md) | Set up a dev environment and run common tasks |

## Project direction

| Doc | Covers |
| --- | --- |
| [`ROADMAP.md`](ROADMAP.md) | What is intentionally not built yet and the next 90 days |
| [`ETHICS.md`](ETHICS.md) | Data provenance, public-sector responsibility, limitations |
| [`RELEASE_NOTES.md`](RELEASE_NOTES.md) | How to tag a release |

## Demo + portfolio

| Doc | Covers |
| --- | --- |
| [`SCREENSHOTS.md`](SCREENSHOTS.md) | Walkthrough order to capture for the portfolio gallery |
| [`screenshots/README.md`](screenshots/README.md) | How to regenerate screenshots with Playwright |
| [`TALKING_POINTS.md`](TALKING_POINTS.md) | Interview-ready narratives and expected questions |

## API reference

| Asset | What it is |
| --- | --- |
| [`openapi.json`](openapi.json) | Committed OpenAPI snapshot; regenerate with `python -m app.scripts.dump_openapi` |
| `http://localhost:8000/docs` | Interactive Swagger UI when the API is running |
| `http://localhost:8000/redoc` | ReDoc alternative |

## Assets

| Asset | Purpose |
| --- | --- |
| [`assets/logo.svg`](assets/logo.svg) | Project logo — used by the top-level README header |
