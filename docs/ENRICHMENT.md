# Enrichment

The enrichment layer turns raw procurement notices into something an
analyst can skim, compare, and audit. It runs **offline by default** — no
LLM, no external API — so the portfolio demo is reproducible, free to
run, and green in CI.

## Pipeline

```
Opportunity ──► text normalization ──► keyword / date / entity extraction
                                       ▼
                                 taxonomy tagging
                                       ▼
                         rule-based scoring + rationale
                                       ▼
                         price anomaly (from item prices)
                                       ▼
                         provider.summarize(title, body)
                                       ▼
                         TF-IDF hashed fingerprint (stable MD5)
                                       ▼
                                 Enrichment row
```

## Scoring — explainable by design

Every score lives in [`apps/api/app/enrichment/scoring.py`](../apps/api/app/enrichment/scoring.py).
Each rule that fires contributes both a weight and a short human-readable
reason; reasons are persisted on `enrichments.entities.score_rationale`
and surfaced on the opportunity detail page, under the score bar.

| Signal | Ground truth |
| --- | --- |
| Complexity | +0.10 per tech term (up to 4) · +0.08 per 1500-char bucket of body (up to 4) · +0.10 if ≥5 items |
| Effort | +0.05 per item (up to 8) · +0.5 × log10(value)/9 (saturates near R$ 1B) |
| Risk | +0.25 if dispensa/inexigibilidade · +0.30 if deadline ≤ 5d, +0.20 if ≤ 8d, +0.10 if ≤ 15d · +0.15 on urgency keyword · +0.10 if items have no reference prices |
| Price anomaly | `clip(0.1 + 0.6 · log1p(IQR/median), 0, 1)` — robust to outliers |

A procurement analyst can open the file, disagree with a rule, edit the
weight, and commit the change. That's the point.

### Example rationale in the API

```json
{
  "enrichment": {
    "complexity_score": 0.62,
    "risk_score": 0.85,
    "entities": {
      "score_rationale": {
        "complexity": [
          "2 termo(s) técnico(s) detectado(s) (+0.20)",
          "objeto longo (+0.16)"
        ],
        "risk": [
          "modalidade dispensa (+0.25)",
          "prazo muito curto (4d) (+0.30)",
          "linguagem de urgência: emergencial (+0.15)"
        ]
      }
    }
  }
}
```

## Taxonomy

[`apps/api/app/enrichment/taxonomy.py`](../apps/api/app/enrichment/taxonomy.py)
is a small, editable keyword-to-category map across 11 buckets
(Tecnologia, Saúde, Educação, Obras, Segurança, Transporte, Alimentação,
Serviços Gerais, Materiais, Meio Ambiente, Consultoria). It is not a
classifier — it's an explicit lookup table that flags intents and lets
the UI surface useful facets. Adding a category is editing a dict.

## Summarization

The default `OfflineProvider` returns:

- a two-sentence lede extracted from the body (split on terminal
  punctuation followed by a capital letter so abbreviations like
  "S.A." don't truncate mid-sentence);
- up to five bullets that call out detected signals: pregão /
  credenciamento / dispensa / urgência / lotes / registro de preços /
  menor preço, plus the top six keywords.

The `Provider` protocol in
[`apps/api/app/enrichment/providers.py`](../apps/api/app/enrichment/providers.py)
defines the integration surface. Setting `ENRICHMENT_MODE=llm` plus
`LLM_PROVIDER` / `LLM_API_KEY` / `LLM_MODEL` swaps in a real LLM without
changing any call site.

### Example: bringing your own LLM

```python
# apps/api/app/enrichment/providers.py
class AnthropicProvider:
    name = "llm/anthropic"
    model = "claude-sonnet-4-5"

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

Wire it up in `get_provider()` and set `LLM_PROVIDER=anthropic`.

## Similarity — why hashed TF-IDF

We use a 1024-bucket hashed TF-IDF with an L2-normalized cosine. For a
corpus of a few thousand short Portuguese notices, that's both accurate
enough to surface useful neighbors and cheap enough to run without a
GPU or an embeddings service.

The bucket function is **MD5-based**. Python's built-in `hash()` is
randomized per process (`PYTHONHASHSEED=random` by default), which would
mean that a fingerprint persisted today would silently map to different
buckets tomorrow and every similarity query would return garbage. That
regression used to be in this repo — see
[`apps/api/tests/test_fingerprint.py`](../apps/api/tests/test_fingerprint.py)
for the subprocess-level guard against it reappearing.

### Scaling plan

When the corpus passes ~10k notices, migrate to pgvector:

1. Add pgvector to `infra/docker-compose.yml`.
2. Add a `vector(1024)` column to `enrichments`.
3. Swap `SimilarityIndex.top_k` for `ORDER BY fingerprint <-> :q`.

The fingerprint column was deliberately designed as a drop-in target:
today it's JSON, tomorrow it's a dense vector.

## Ethics

Every score and tag is produced by rules you can read. No model
hallucinates a risk number. The provider abstraction makes it explicit
whether a human-readable summary came from deterministic rules or from a
third-party LLM call; the `provider` and `model` columns on the
`enrichments` table preserve that provenance for every row, forever.
