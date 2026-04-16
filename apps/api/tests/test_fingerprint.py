"""Ensure the TF-IDF fingerprint bucketing is stable across processes.

This guards against the previous bug where Python's hash() randomization
invalidated stored fingerprints on every restart.
"""

from __future__ import annotations

import subprocess
import sys


def test_stable_bucket_identical_across_python_processes():
    """stable_bucket(t) must produce the same int regardless of PYTHONHASHSEED."""
    code = "from app.utils.text import stable_bucket; print(stable_bucket('medicamentos'))"
    out1 = subprocess.check_output(
        [sys.executable, "-c", code], env={"PYTHONHASHSEED": "0"}
    ).strip()
    out2 = subprocess.check_output(
        [sys.executable, "-c", code], env={"PYTHONHASHSEED": "1234"}
    ).strip()
    out3 = subprocess.check_output(
        [sys.executable, "-c", code], env={"PYTHONHASHSEED": "random"}
    ).strip()
    assert out1 == out2 == out3


def test_fingerprint_self_similarity_is_one():
    from app.utils.text import cosine, tfidf_fingerprint

    fp = tfidf_fingerprint("software de gestão administrativa")
    assert round(cosine(fp, fp), 4) == 1.0


def test_fingerprint_unrelated_texts_low_similarity():
    from app.utils.text import cosine, tfidf_fingerprint

    a = tfidf_fingerprint("aquisição de medicamentos da farmácia básica")
    b = tfidf_fingerprint("recapeamento asfáltico em vias urbanas")
    assert cosine(a, b) < 0.2
