"""Text normalization + lightweight NLP helpers.

Designed to work offline for deterministic demos. We intentionally avoid
heavyweight NLP deps (spaCy, transformers) to keep the project installable
on modest hardware.

Determinism note: we deliberately do **not** use Python's built-in ``hash()``
to bucket tokens. Python 3 randomizes string hashing per process
(``PYTHONHASHSEED=random``), which would give us different buckets every
time the API restarts and silently break similarity against stored
fingerprints. We use a stable MD5-derived int instead.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from unidecode import unidecode

# Portuguese + Brazilian procurement stopwords. Kept small on purpose — we
# strip the connective glue and legal boilerplate and keep the domain nouns
# (medicamentos, obra, software, …) so they stay as signal.
STOPWORDS_PT: set[str] = {
    # articles, prepositions, pronouns, common verbs
    "a",
    "e",
    "o",
    "as",
    "os",
    "da",
    "de",
    "do",
    "das",
    "dos",
    "em",
    "na",
    "no",
    "nas",
    "nos",
    "para",
    "por",
    "com",
    "sem",
    "um",
    "uma",
    "uns",
    "umas",
    "ao",
    "aos",
    "à",
    "às",
    "que",
    "se",
    "ou",
    "mas",
    "é",
    "são",
    "ser",
    "foi",
    "sobre",
    "entre",
    "até",
    "após",
    "ante",
    "este",
    "esta",
    "isso",
    "isto",
    "esse",
    "essa",
    "pela",
    "pelo",
    "pelas",
    "pelos",
    "the",
    "of",
    "and",
    # procurement boilerplate — ubiquitous, low signal
    "licitação",
    "edital",
    "lote",
    "item",
    "quantidade",
    "valor",
    "preço",
    "empresa",
    "empresas",
    "órgão",
    "secretaria",
    "referente",
    "conforme",
    "objeto",
    "presente",
    "contratação",
}

_PUNCT_RE = re.compile(r"[^a-z0-9\sáéíóúâêôãõç]", re.IGNORECASE)
_WS_RE = re.compile(r"\s+")
_MONEY_RE = re.compile(r"r\$?\s*[\d\.\,]+", re.IGNORECASE)


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    if not text:
        return ""
    x = text.strip().lower()
    x = _PUNCT_RE.sub(" ", x)
    x = _WS_RE.sub(" ", x)
    return x.strip()


def tokens(text: str, *, min_len: int = 3) -> list[str]:
    """Tokenize text into content words, removing stopwords + accents."""
    normalized = normalize(text)
    raw = [unidecode(t) for t in normalized.split()]
    stop_norm = {unidecode(s) for s in STOPWORDS_PT}
    return [t for t in raw if len(t) >= min_len and t not in stop_norm and not t.isdigit()]


def top_keywords(text: str, *, k: int = 10) -> list[str]:
    counter = Counter(tokens(text))
    return [w for w, _ in counter.most_common(k)]


def extract_money_candidates(text: str) -> list[str]:
    """Return raw string matches that look like R$ money amounts."""
    if not text:
        return []
    return [m.group(0).strip() for m in _MONEY_RE.finditer(text)]


# ---------------------------------------------------------------------------
# Tiny hashed TF-IDF fingerprint — offline similarity without external deps.
# ---------------------------------------------------------------------------
VEC_DIM: int = 1024
"""Bucket count for the hashing trick. 1024 keeps collisions rare on a few
thousand short Portuguese documents while staying trivially serializable."""


def stable_bucket(token: str, dim: int = VEC_DIM) -> int:
    """Deterministic token → bucket index.

    Uses MD5 rather than ``hash()`` because Python randomizes string hashing
    per process — which would silently invalidate every fingerprint we
    previously persisted.
    """
    digest = hashlib.md5(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % dim


def tfidf_fingerprint(
    text: str,
    corpus_df: dict[str, int] | None = None,
    n_docs: int = 1,
) -> dict[str, float]:
    """Build a sparse, L2-normalized TF-IDF vector as ``{bucket_index: weight}``.

    ``corpus_df`` maps tokens to the number of documents each appears in. When
    ``corpus_df`` is None, IDF collapses to 1.0 (pure TF).
    """
    toks = tokens(text)
    if not toks:
        return {}
    tf = Counter(toks)
    out: dict[int, float] = {}
    total = sum(tf.values())
    for tok, freq in tf.items():
        tf_w = freq / total
        if corpus_df and tok in corpus_df:
            idf = math.log((1 + n_docs) / (1 + corpus_df[tok])) + 1.0
        else:
            idf = 1.0
        bucket = stable_bucket(tok)
        out[bucket] = out.get(bucket, 0.0) + tf_w * idf
    norm = math.sqrt(sum(v * v for v in out.values())) or 1.0
    return {str(k): round(v / norm, 6) for k, v in out.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two pre-normalized TF-IDF dicts."""
    if not a or not b:
        return 0.0
    # both vectors are L2-normalized, so a · b == cos(a, b)
    return sum(a.get(k, 0.0) * v for k, v in b.items())
