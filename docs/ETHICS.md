# Ethics, data quality, and limitations

LicitScope consumes **public** Brazilian procurement data. Even public
data carries responsibilities — this page documents how we think about
them.

## Data sources & licensing

| Source | License / basis | Used here? |
| --- | --- | --- |
| PNCP — Portal Nacional de Contratações Públicas | Federal public data; API is open without authentication | **Yes** |
| Portal da Transparência | Federal public data | Roadmap only |
| Compras.gov.br (dados.gov.br) | Federal open data | Roadmap only |

All queries are made with a polite `User-Agent` that identifies the client
as `LicitScope/0.1 (+https://github.com/licitscope)`, with conservative
page sizes and exponential backoff. No attempt is made to evade rate
limits or authentication.

## Personally identifiable information (PII)

- Officials, servants, citizens: **LicitScope does not store PII beyond
  what the public source already exposes**. In practice, the data we
  persist is agency-level (CNPJ, name, location) and supplier-level
  (CNPJ/CPF, size, CNAE). CPFs are rare in the notice payloads and are
  stored only when the source itself publishes them.
- If a user reports that their personal data is exposed, we remove it
  on request — see CONTRIBUTING.md for the contact channel.

## Synthetic demo data

The `data-demo/` fixtures are **entirely synthetic**. CNPJs, suppliers,
and notice contents were generated with a seeded PRNG and plausible
templates. They are meant to be *shape-faithful*, not *truth-faithful*.
Do not cite any figure from a demo run as a factual record of Brazilian
public procurement.

## Heuristic, not authoritative

- The **risk score** is a rule-based signal meant to help an analyst
  triage their reading queue. It is not an accusation of fraud.
- The **price anomaly score** flags dispersion; it does not prove
  overpricing. Market segmentation, regional differences, and product
  tiering all produce legitimate dispersion.
- The **AI summary** (offline mode) is deterministic and extractive; it
  never invents facts. If you swap in an LLM provider, clearly surface
  that in the UI and expect occasional hallucination.

## Reproducibility

- `scripts/generate_fixtures.py` is seeded (`random.seed(42)`).
- All scoring rules are pure Python with no randomness.
- TF-IDF fingerprints depend only on the text and a stable hash.

Given the same DB state, two runs produce identical enrichment output.

## Operational notes

- **Raw payloads** are stored forever. If the source later redacts a
  notice, our copy may still reflect the prior state. This is by design
  — procurement accountability requires history — but make sure your
  deployment respects local data-retention requirements.
- **Watchlists** are unauthenticated in the MVP; do not expose the API
  to the public internet without adding auth first.
