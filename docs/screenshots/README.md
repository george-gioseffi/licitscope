# Screenshots

The PNG files in this directory are committed artefacts rendered in the
top-level [`README.md`](../../README.md) gallery. They are regenerated
deterministically by a Playwright script — refresh them whenever the UI
changes meaningfully so the README never drifts away from the app.

## Regenerate

```bash
# 1. Start the full stack somewhere the browser can reach:
make up                                   # docker compose, or
make api & make web                       # local SQLite mode

# 2. One-off: install Playwright + Chromium inside apps/web:
cd apps/web
npm i -D @playwright/test
npx playwright install chromium

# 3. Take the shots (run from apps/web so Node resolves @playwright/test):
node scripts/take_screenshots.mjs \
    --base=http://127.0.0.1:3000 \
    --out=../../docs/screenshots
```

Re-commit the updated PNGs in the same change that updates the UI.

## What ships here

| File                          | Page                                               |
| ----------------------------- | -------------------------------------------------- |
| `01-dashboard.png`            | `/` — executive overview (hero image in README)    |
| `02-opportunities.png`        | `/opportunities?state=SP&sort=value_desc` — feed   |
| `03-search.png`               | `/search?q=medicamentos` — semantic search         |
| `04-contracts-pricing.png`    | `/contracts` — pricing dispersion + contracts      |
| `05-agencies.png`             | `/agencies` — agency directory                     |
| `06-watchlists.png`           | `/watchlists` — saved filters                      |
| `07-health.png`               | `/health` — source-health dashboard                |
| `08-about.png`                | `/about` — project, sources, IA                    |
| `09-opportunity-detail.png`   | `/opportunities/{first-id}` — detail page          |

Keep file names stable — they are referenced verbatim from the README
gallery section.

## Capture settings

Headless Chromium at **1440 × 900 @ 2× dpr**, `colorScheme: "dark"`,
`locale: "pt-BR"`, `waitUntil: "networkidle"` plus an extra 800 ms settle
so charts and lazy-loaded queries have time to render.
