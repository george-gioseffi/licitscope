# Changelog

All notable changes to this project are documented here. The format is
based on [Keep a Changelog](https://keepachangelog.com/) and the project
follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Inline price distribution widget on the pricing page (min–max track
  with IQR fill and median tick).
- Per-rule scoring rationale persisted on `enrichments.entities.score_rationale`
  and rendered under each signal on the opportunity detail page.
- Pre-commit hooks (`trailing-whitespace`, `end-of-file-fixer`, `ruff`,
  `ruff-format`, `check-yaml`, `check-json`, `check-added-large-files`).
- EditorConfig for consistent indent / EOL / charset across editors.
- Weekly CodeQL workflow for Python and JavaScript.
- CI step that regenerates `data-demo/` and fails on drift.
- Tests: 22 new tests covering pricing, filters, repo upserts, and
  fingerprint stability across Python processes (49 → 71).
- `ChevronLeft` / `ChevronRight` pagination controls on the feed.
- `SORT_OPTIONS` constant + validator that rejects unknown sort values.

### Changed
- TF-IDF bucketing switched from Python's randomized `hash()` to a
  stable MD5 derivation. Fingerprint bucket count 256 → 1024.
- Price anomaly switched from raw standard deviation to an IQR-based
  coefficient of dispersion (robust to outliers).
- Pricing service uses `statistics.quantiles(..., n=4)` instead of
  naïve index-based percentiles.
- Anomaly flag threshold: `IQR / median >= 0.75` (consistent with the
  enrichment-side scoring).
- Ingestion persists raw payloads **before** upserts, so parser/upsert
  failures still leave a complete replay trail.
- Ingestion skips payloads with empty `source_id` (counted as
  `skipped`, not silently dropped).
- `OpportunityFilters` validates & normalizes: state upper-cased,
  strings trimmed, sort whitelisted, negative value bounds rejected.
- Facet queries now exclude their own dimension from the WHERE clause
  so the UI shows alternatives, not tautologies.
- Dashboard `top_agencies` rewritten as a single join (no N+1).
- Supplier profile `top_agencies` now includes name and state.
- KPI labels translated to Portuguese to match the rest of the UI.
- Opportunities feed rendered as a proper responsive grid (was two
  sliced columns); paginated with `page`/`page_size` URL params.
- Opportunity cards surface a "risco alto" badge when `risk_score >= 0.7`.
- Offline summary splits sentences on terminal punctuation followed by
  a capital letter (preserves abbreviations like "S.A.").
- Fixture generator derives unit prices from anchor prices per item
  description (±18% noise) so pricing distributions look credible.
- Fixture CATMAT bucketing uses MD5 for byte-stable regeneration.

### Fixed
- Validation errors in `_filters_dep` now return 422 with JSON-serializable
  detail, not 500.
- `min_value > max_value` is rejected with a clear 422 instead of an
  empty result page.
- Sidebar dead spacer div removed; `className` typo (`class=`) eliminated.
- Dashboard "recent" entries now eager-load agency + enrichment so
  risk/complexity signals are populated (were silently always None).

### Security
- Pipeline pins `PYTHONHASHSEED=0` in CI and runs CodeQL weekly.
- `npm ci` enforces the lockfile; pre-commit blocks files >512 KB.

### Docs
- README rewritten to drop "AI-generated summaries" and other inflated
  language. Clear separation between integrated (PNCP) and roadmap
  sources.
- ENRICHMENT.md documents every scoring rule by weight + signal source.
- TALKING_POINTS.md expanded with the new trade-offs (IQR anomaly,
  facet dimension exclusion, MD5 bucketing).

[Unreleased]: https://github.com/george-gioseffi/licitscope
