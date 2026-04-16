from app.utils.text import cosine, normalize, tfidf_fingerprint, tokens, top_keywords


def test_normalize_removes_punctuation():
    assert normalize("Aquisição, de  medicamentos!") == "aquisição de medicamentos"


def test_tokens_removes_stopwords_and_accents():
    result = tokens("Aquisição de medicamentos para o hospital de Campinas")
    assert "medicamentos" in result
    assert "hospital" in result
    assert "de" not in result


def test_top_keywords_stable_order_for_deterministic_input():
    text = "medicamento hospital medicamento hospital medicamento"
    assert top_keywords(text, k=2)[0] == "medicamento"


def test_fingerprint_cosine_self_is_one():
    fp = tfidf_fingerprint("contratação de software de gestão administrativa")
    assert round(cosine(fp, fp), 2) == 1.00


def test_fingerprint_cosine_related_has_nonzero_score():
    a = tfidf_fingerprint("aquisição de medicamentos farmácia básica")
    b = tfidf_fingerprint("medicamentos para farmácia municipal")
    score = cosine(a, b)
    assert score > 0.0
