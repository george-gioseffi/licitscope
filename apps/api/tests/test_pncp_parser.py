from app.clients.pncp_parser import parse_agency, parse_full, parse_items, parse_opportunity

SAMPLE = {
    "numeroControlePNCP": "46395000000139-1-001234/2026",
    "numeroCompra": "050/2026",
    "modalidadeId": 1,
    "situacaoCompraNome": "Divulgada",
    "objetoCompra": "Aquisição de medicamentos",
    "informacaoComplementar": "Detalhes completos do objeto...",
    "valorTotalEstimado": 1_250_000.0,
    "dataPublicacaoPncp": "2026-04-10T10:00:00",
    "dataAberturaProposta": "2026-04-11T09:00:00",
    "dataEncerramentoProposta": "2026-04-28T17:00:00",
    "linkSistemaOrigem": "https://example.org/edital",
    "orgaoEntidade": {
        "cnpj": "46395000000139",
        "razaoSocial": "Prefeitura Municipal de São Paulo",
        "nomeFantasia": "PMSP",
        "esferaId": "municipal",
        "poderId": "executivo",
    },
    "unidadeOrgao": {"ufSigla": "SP", "municipioNome": "São Paulo", "codigoIbge": "3550308"},
    "itens": [
        {
            "numeroItem": 1,
            "descricao": "Dipirona 500mg",
            "unidadeMedida": "comprimido",
            "quantidade": 10000,
            "valorUnitarioEstimado": 0.45,
            "valorTotal": 4500.0,
            "codigoItemCatalogo": "BR12345",
        }
    ],
}


def test_parse_agency_maps_core_fields():
    agency = parse_agency(SAMPLE)
    assert agency["cnpj"] == "46395000000139"
    assert agency["name"] == "Prefeitura Municipal de São Paulo"
    assert agency["state"] == "SP"
    assert agency["sphere"] == "municipal"


def test_parse_opportunity_assigns_pncp_modality_and_status():
    opp = parse_opportunity(SAMPLE)
    assert opp["modality"] == "pregao_eletronico"
    assert opp["status"] == "published"
    assert opp["estimated_value"] == 1_250_000.0
    assert opp["source"] == "pncp"
    assert opp["pncp_control_number"] == "46395000000139-1-001234/2026"


def test_parse_items_normalizes_fields():
    items = parse_items(SAMPLE)
    assert items and items[0]["description"] == "Dipirona 500mg"
    assert items[0]["unit"] == "comprimido"
    assert items[0]["catmat_code"] == "BR12345"


def test_parse_full_returns_tuple():
    agency, opp, items = parse_full(SAMPLE)
    assert agency and opp and len(items) == 1


def test_unknown_modality_defaults_to_outros():
    payload = dict(SAMPLE)
    payload["modalidadeId"] = 999
    assert parse_opportunity(payload)["modality"] == "outros"
