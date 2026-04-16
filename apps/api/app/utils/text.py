"""Text normalization + lightweight NLP helpers.

Designed to work offline for deterministic demos. We intentionally avoid
heavyweight NLP deps (spaCy, transformers) to keep the project installable
on modest hardware.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from unidecode import unidecode

# Portuguese + Brazilian procurement stopwords. Enough to de-noise signals
# without fancy language models.
STOPWORDS_PT: set[str] = {
    "a", "e", "o", "as", "os", "da", "de", "do", "das", "dos", "em", "na", "no",
    "nas", "nos", "para", "por", "com", "sem", "um", "uma", "uns", "umas", "ao",
    "aos", "à", "às", "que", "se", "ou", "mas", "é", "são", "ser", "foi",
    "sobre", "entre", "até", "após", "ante", "este", "esta", "isso", "isto",
    "esse", "essa", "pela", "pelo", "pelas", "pelos", "the", "of", "and",
    "licitação", "edital", "lote", "item", "quantidade", "valor", "preço",
    "empresa", "empresas", "órgão", "secretaria",
    # short connectives and legal boilerplate only — we intentionally keep
    # domain nouns like "medicamentos", "obra", "software" as signal words.
    "referente", "conforme", "objeto", "presente",
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
_VEC_DIM = 256


def _hash(tok: str) -> int:
    # deterministic bucket per token
    return hash(tok) % _VEC_DIM


def tfidf_fingerprint(text: str, corpus_df: dict[str, int] | None = None, n_docs: int = 1) -> dict[str, float]:
    """Build a sparse TF-IDF vector as {bucket_index: weight}.

    This is a heuristic: `corpus_df` is a document-frequency map from tokens
    to the number of documents each appears in. When ``corpus_df`` is None,
    we fall back to raw TF.
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
        out[_hash(tok)] = out.get(_hash(tok), 0.0) + tf_w * idf
    # L2-normalize
    norm = math.sqrt(sum(v * v for v in out.values())) or 1.0
    return {str(k): round(v / norm, 6) for k, v in out.items()}


def cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    # Vectors are already L2-normalized.
    return sum(a.get(k, 0.0) * v for k, v in b.items())
