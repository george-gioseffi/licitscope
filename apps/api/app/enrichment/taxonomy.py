"""Keyword-based taxonomy for classifying procurement notices.

This is an intentionally small, editable taxonomy — it is not an ML model.
It gives us deterministic, explainable category tags out of the box and is
easy to extend by editing the mapping below.
"""

from __future__ import annotations

from unidecode import unidecode

TAXONOMY: dict[str, list[str]] = {
    "Tecnologia da Informação": [
        "software", "sistema", "ti", "tecnologia", "nuvem", "cloud",
        "datacenter", "servidor", "licença", "licenca", "saas", "erp",
        "rede", "firewall", "antivirus", "notebook", "computador",
        "informatica", "cibersegurança", "ciberseguranca", "desenvolvimento",
    ],
    "Saúde": [
        "saude", "hospital", "medicamento", "medicamentos", "farmacia",
        "farmaceutico", "clinica", "medico", "medica", "equipamento medico",
        "ambulatorial", "vacina", "insumo hospitalar", "seringa", "ortopedico",
    ],
    "Educação": [
        "educacao", "escola", "ensino", "estudante", "aluno", "universidade",
        "uniformes", "merenda", "livro didatico", "material escolar",
        "professor", "professora", "creche",
    ],
    "Obras e Engenharia": [
        "obra", "construcao", "pavimentacao", "asfalto", "reforma",
        "engenharia", "drenagem", "recapeamento", "ponte", "edificacao",
        "saneamento", "esgoto", "agua potavel", "terraplenagem", "concreto",
    ],
    "Segurança Pública": [
        "seguranca publica", "policia", "militar", "viatura", "armamento",
        "colete balistico", "municoes", "monitoramento", "cftv",
    ],
    "Transporte e Frota": [
        "veiculo", "caminhao", "onibus", "frota", "transporte",
        "locacao de veiculos", "combustivel", "gasolina", "diesel",
        "manutencao automotiva", "pneu",
    ],
    "Alimentação": [
        "alimentacao", "refeicao", "merenda", "nutricao", "arroz",
        "feijao", "leite", "cesta basica", "carne",
    ],
    "Serviços Gerais": [
        "limpeza", "seguranca patrimonial", "vigilancia", "portaria",
        "copeiragem", "conservacao", "jardinagem",
    ],
    "Materiais de Escritório": [
        "material de escritorio", "papel a4", "toner", "cartucho",
        "papelaria", "caneta", "agenda",
    ],
    "Meio Ambiente": [
        "residuos", "reciclagem", "ambiental", "licenciamento ambiental",
        "coleta seletiva", "sustentabilidade",
    ],
    "Consultoria e Assessoria": [
        "consultoria", "assessoria", "auditoria", "treinamento",
        "capacitacao", "pesquisa", "estudo",
    ],
}

# Precompute normalized tokens for matching.
_NORMALIZED: dict[str, list[str]] = {
    category: [unidecode(term.lower()) for term in terms]
    for category, terms in TAXONOMY.items()
}


def classify(text: str, top_k: int = 3) -> list[str]:
    """Return the top-k categories whose keywords appear in ``text``."""
    if not text:
        return []
    haystack = unidecode(text.lower())
    scores: list[tuple[str, int]] = []
    for category, terms in _NORMALIZED.items():
        hits = sum(1 for term in terms if term in haystack)
        if hits:
            scores.append((category, hits))
    scores.sort(key=lambda x: (-x[1], x[0]))
    return [name for name, _ in scores[:top_k]]
