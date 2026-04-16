# Enrichment

The enrichment layer turns raw procurement notices into something an
analyst can skim and compare. It is designed to work **offline** by default
— no LLM, no external API — so the portfolio demo remains fully
reproducible and free to run.

## Pipeline

```
Opportunity ──► text normalization ──► keyword / date / entity extraction
                                       ▼
                                 taxonomy tagging
                                       ▼
                        heuristic scoring (complexity, effort, risk)
                                       ▼
                           price anomaly (from item prices)
                                       ▼
                           LLM or offline summarizer
                                       ▼
                        TF-IDF hashed fingerprint
                                       ▼
                                 Enrichment row
```

## Scoring rules (explainable on purpose)

Each score is a float in [0, 1]. The rules live in
`apps/api/app/enrichment/scoring.py`, encoded so a procurement analyst can
critique, edit, and PR improvements.

| Signal | Rule |
| --- | --- |
| Complexity | Baseline 0.30, +0.10 per tech-term hit (up to 4), +0.08 per 1500 chars |
| Effort | Baseline 0.25, +0.05 per item, +0.5 × log10(value)/9 |
| Risk | Baseline 0.30; +0.25 for dispensa/inexigibilidade; +0.25 for deadlines ≤ 8d; +0.15 for urgência keywords |
| Price anomaly | From dispersion of per-unit prices: `clip(0.1 + 0.6·log1p(CV), 0, 1)` |

This gives a **defensible, reproducible** score that a reviewer can trace
without unpacking a neural network.

## Taxonomy

The taxonomy at `apps/api/app/enrichment/taxonomy.py` is a small, editable
keyword-to-category map across 11 buckets (Tecnologia, Saúde, Educação,
Obras, Segurança, Transporte, Alimentação, Serviços Gerais, Materiais,
Meio Ambiente, Consultoria). It is not a classifier — it's a signal that
flags intents and lets the UI surface useful facets without training
anything.

## Summarization

The default provider (`OfflineProvider`) returns:

- a two-sentence lede extracted from the body
- up to five bullet points that mention the detected signals
  (modality, urgency, lot structure, top keywords)

The `Provider` protocol in `apps/api/app/enrichment/providers.py` exists
so that an LLM-backed summarizer can be swapped in at will. The app
reads `ENRICHMENT_MODE` (`offline` / `llm`) and `LLM_PROVIDER` to decide.

### Example: bringing your own LLM

```python
# apps/api/app/enrichment/providers.py
class AnthropicProvider:
    name = "llm/anthropic"
    model = "claude-sonnet-4-6"

    def summarize(self, *, title, body):
        resp = anthropic.messages.create(
            model=self.model,
            max_tokens=400,
            system=PROMPT,
            messages=[{"role": "user", "content": f"{title}\n\n{body}"}],
        )
        summary, bullets = parse_response(resp.content)
        return summary, bullets
```

Hook it up in `get_provider()` and set `LLM_PROVIDER=anthropic`.

## Similarity (semantic search)

We use a hashed TF-IDF fingerprint in 256 buckets. For a corpus of a few
thousand notices this is both accurate enough to surface useful matches
and cheap enough to run without GPU / embeddings services.

When you scale past 10k notices:

1. Add pgvector to the docker-compose.
2. Add a `vector` column to `enrichments`.
3. Swap `SimilarityIndex.top_k` with a pgvector `ORDER BY fingerprint <-> :q`.

The fingerprint field was chosen to be a drop-in: today it's JSON, tomorrow
it's a dense vector.

## Ethics

Every score and tag is produced by rules you can read. No model
hallucinates a risk number. The provider abstraction makes it explicit
whether a human-readable summary came from deterministic rules or from a
third-party LLM call; the `provider` + `model` columns on the `enrichments`
table preserve the provenance forever.
