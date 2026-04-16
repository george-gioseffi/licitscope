# Contributing to LicitScope

Thank you for considering a contribution. This project is a portfolio-grade
open-source platform built on public Brazilian procurement data, and we are
happy to accept improvements from the community.

## Before you start

- Please read the top-level [README](./README.md) and the architecture notes
  under [`docs/`](./docs). It helps avoid duplicate proposals.
- For significant changes (new endpoints, new tables, data-model changes),
  open an issue first describing the intent — it is much easier to iterate on
  direction than on a finished PR.

## Developer setup

```bash
# one-shot setup (creates .venv, installs deps, seeds demo DB)
./scripts/dev-setup.sh

# run the stack
make api    # backend on :8000
make web    # frontend on :3000
```

All backend changes must pass:

```bash
cd apps/api
ruff check app tests
pytest -q
```

Frontend changes must pass:

```bash
cd apps/web
npm run lint
npm run typecheck
npm run build
```

## Coding guidelines

- **Backend**: Pydantic 2 / SQLModel idioms, service layer separate from routes,
  repositories own SQL. Keep it explicit.
- **Frontend**: prefer small, composable components; no cleverness for its
  own sake. Tailwind utility classes > bespoke CSS.
- **Tests**: favour tests that exercise real code paths — use bundled fixtures
  rather than mocking the world.
- **Commits**: small, descriptive, present tense.
- **Docs**: if you added a new feature, add a line in the appropriate
  `docs/*.md` file.

## Data sources & ethics

LicitScope consumes public Brazilian procurement data (PNCP, Portal da
Transparência, Compras.gov.br). By contributing you agree to honor the terms
of use of these sources and to avoid code that:

- tries to circumvent authentication or rate-limits;
- stores personally identifiable information beyond what is already public;
- uses the platform to target individuals.

## License

By submitting a contribution you agree to license it under the MIT License
that covers the rest of the project.
