# LicitScope — demo data

This folder contains **deterministic, synthetic procurement fixtures** that
mirror the shape of real PNCP payloads and let the platform be explored
end-to-end without calling any live API.

| File | Purpose |
| --- | --- |
| `agencies.json` | 20 realistic federal / estadual / municipal contracting bodies |
| `suppliers.json` | 15 suppliers across TI, saúde, obras, serviços gerais |
| `opportunities.json` | 85 procurement notices across 9 categories, 6 modalities, 6 statuses |
| `contracts.json` | Signed contracts linking opportunities ↔ suppliers |
| `pncp/opportunities.json` | Same notices repackaged in **PNCP-compatible** JSON so the ingestion pipeline can be exercised end-to-end offline |

## Provenance

All CNPJs, supplier identities, and values are **fabricated for demo
purposes** but generated from plausible Brazilian templates (RENAME drug
lists, realistic CATMAT codes, UBS construction, hemodiálise credentialing,
etc.). Nothing here should be treated as a factual record of a real
procurement action.

## Regeneration

The fixtures are reproducible. To regenerate from scratch:

```bash
python scripts/generate_fixtures.py
```

The generator is seeded (`random.seed(42)`) so output is byte-stable.

## Swapping in real data

The same JSON shapes are accepted by `app/scripts/seed.py`. To seed with
real PNCP data, run `python -m app.scripts.run_ingestion` with
`INGESTION_USE_FIXTURES=false` — the ingestion service hits the live PNCP
API and falls back to this folder only if the API is unreachable.
