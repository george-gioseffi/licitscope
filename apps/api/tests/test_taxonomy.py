from app.enrichment.taxonomy import classify


def test_classify_it_notice():
    assert "Tecnologia da Informação" in classify(
        "Contratação de software ERP e serviços de computação em nuvem para servidor"
    )


def test_classify_obras_notice():
    assert "Obras e Engenharia" in classify(
        "Execução de recapeamento asfáltico e drenagem urbana em vias municipais"
    )


def test_classify_empty_text():
    assert classify("") == []


def test_classify_returns_topk():
    # Contains terms for both "Saúde" and "Educação" — we only want <= top_k.
    tags = classify(
        "Aquisição de merenda escolar para rede municipal de ensino com equipamentos médicos",
        top_k=2,
    )
    assert len(tags) <= 2
