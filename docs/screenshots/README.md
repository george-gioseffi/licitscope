# Screenshots

This directory is the landing spot for the portfolio screenshot gallery.
It ships empty in the repo — contributors regenerate the images locally
and commit them when preparing a release.

## Regenerate

```bash
# 1. Start the full stack somewhere the browser can reach:
make up                                   # docker compose, or
make api & make web                       # local SQLite mode

# 2. Install Playwright (one-off):
cd apps/web
npm i -D @playwright/test
npx playwright install chromium

# 3. Take the shots:
cd ../..
node scripts/take_screenshots.mjs \
    --base=http://localhost:3000 \
    --out=docs/screenshots
```

The script follows the walkthrough in [`../SCREENSHOTS.md`](../SCREENSHOTS.md)
and produces 9 PNGs:

| File                          | Page                                               |
| ----------------------------- | -------------------------------------------------- |
| `01-dashboard.png`            | `/` — executive overview                           |
| `02-opportunities.png`        | `/opportunities?state=SP&sort=value_desc` — feed   |
| `03-search.png`               | `/search?q=medicamentos` — semantic search         |
| `04-contracts-pricing.png`    | `/contracts` — pricing dispersion + contracts      |
| `05-agencies.png`             | `/agencies` — agency directory                     |
| `06-watchlists.png`           | `/watchlists` — saved filters                      |
| `07-health.png`               | `/health` — source-health dashboard                |
| `08-about.png`                | `/about` — project, sources, IA                    |
| `09-opportunity-detail.png`   | `/opportunities/{first-id}` — detail page          |

Keep the file names stable — they are referenced from the top-level
README gallery block.

## Why we don't commit the PNGs

- Binary assets bloat the repo and churn on every UI change.
- Every reviewer wants fresh screenshots that reflect today's UI, not
  whatever version the last committer captured.
- GitHub's social-preview image is uploaded separately through repo
  settings, not through the tree.

If you are preparing a tagged release, commit the generated PNGs under
this folder as part of the release PR.
