"""Generate deterministic, realistic demo fixtures for LicitScope.

This produces ``data-demo/*.json`` + ``data-demo/pncp/opportunities.json``
with a representative cross-section of Brazilian public procurement data:
agencies spanning the three spheres (federal / estadual / municipal),
suppliers with realistic CNAE + location distribution, opportunities across
multiple modalities and categories, and awarded contracts linking them.

Run:
    python scripts/generate_fixtures.py
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data-demo"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "pncp").mkdir(parents=True, exist_ok=True)

SEED = 42
random.seed(SEED)


# ----------------------------------------------------------------------------
# Static, realistic Brazilian reference data
# ----------------------------------------------------------------------------
AGENCIES = [
    # federal
    ("13756663000171", "Ministério da Gestão e da Inovação em Serviços Públicos", "MGI", "federal", "executivo", "DF", "Brasília"),
    ("00394411000109", "Ministério da Saúde", "MS", "federal", "executivo", "DF", "Brasília"),
    ("00394452000103", "Ministério da Educação", "MEC", "federal", "executivo", "DF", "Brasília"),
    ("33683111000107", "Instituto Federal de São Paulo", "IFSP", "federal", "executivo", "SP", "São Paulo"),
    ("07526557000100", "Universidade Federal de Minas Gerais", "UFMG", "federal", "executivo", "MG", "Belo Horizonte"),
    ("00489828000136", "Empresa Brasileira de Pesquisa Agropecuária", "EMBRAPA", "federal", "executivo", "DF", "Brasília"),
    # estadual
    ("46392130000380", "Secretaria de Estado da Saúde de São Paulo", "SES-SP", "estadual", "executivo", "SP", "São Paulo"),
    ("18715615000160", "Governo do Estado de Minas Gerais", "GovMG", "estadual", "executivo", "MG", "Belo Horizonte"),
    ("42498600000171", "Governo do Estado do Paraná", "GovPR", "estadual", "executivo", "PR", "Curitiba"),
    ("27080571000170", "Secretaria de Estado da Saúde do Rio Grande do Sul", "SES-RS", "estadual", "executivo", "RS", "Porto Alegre"),
    ("14390766000140", "Secretaria de Educação do Estado da Bahia", "SEC-BA", "estadual", "executivo", "BA", "Salvador"),
    ("10832074000155", "Secretaria de Segurança Pública do Ceará", "SSP-CE", "estadual", "executivo", "CE", "Fortaleza"),
    # municipal
    ("46395000000139", "Prefeitura Municipal de São Paulo", "PMSP", "municipal", "executivo", "SP", "São Paulo"),
    ("18715383000140", "Prefeitura Municipal de Belo Horizonte", "PBH", "municipal", "executivo", "MG", "Belo Horizonte"),
    ("42498700000143", "Prefeitura Municipal de Curitiba", "PMC", "municipal", "executivo", "PR", "Curitiba"),
    ("27080619000160", "Prefeitura Municipal de Porto Alegre", "PMPA", "municipal", "executivo", "RS", "Porto Alegre"),
    ("13927801000149", "Prefeitura Municipal de Campinas", "PMC-SP", "municipal", "executivo", "SP", "Campinas"),
    ("13381447000130", "Prefeitura Municipal de Fortaleza", "PMF", "municipal", "executivo", "CE", "Fortaleza"),
    ("14390500000116", "Prefeitura Municipal de Salvador", "PMS", "municipal", "executivo", "BA", "Salvador"),
    ("33649282000108", "Prefeitura Municipal do Rio de Janeiro", "PMR", "municipal", "executivo", "RJ", "Rio de Janeiro"),
]

SUPPLIERS = [
    # tax_id, name, trade_name, state, city, size, cnae
    ("07919473000174", "Tech Solutions Brasil S.A.", "TechSol", "SP", "São Paulo", "grande porte", "6203100"),
    ("20738832000141", "MedPharma Distribuidora Ltda", "MedPharma", "SP", "Guarulhos", "grande porte", "4644301"),
    ("19381117000121", "Construtora Horizonte Ltda", "Horizonte", "MG", "Belo Horizonte", "grande porte", "4120400"),
    ("30102117000134", "Segurança Patrimonial Nacional S/A", "SegPat", "RJ", "Rio de Janeiro", "grande porte", "8011101"),
    ("18713919000198", "Papelaria Integrada Ltda", "PapInt", "PR", "Curitiba", "EPP", "4761003"),
    ("27081108000130", "Transporte & Logística Sul Ltda", "TranSul", "RS", "Porto Alegre", "EPP", "4930203"),
    ("14391099000152", "Alimentos Nordeste Ltda", "AliNor", "BA", "Salvador", "ME", "4637102"),
    ("23456789000100", "CloudBR Serviços de TI S/A", "CloudBR", "SP", "Campinas", "grande porte", "6311900"),
    ("11223344000155", "EngCivil Consultoria Ltda", "EngCivil", "DF", "Brasília", "EPP", "7112000"),
    ("55667788000166", "Frota Nacional Veículos S/A", "FrotaN", "MG", "Contagem", "grande porte", "4511101"),
    ("99887766000177", "LimpaBem Serviços Gerais Ltda", "LimpaBem", "RJ", "Rio de Janeiro", "EPP", "8121400"),
    ("66778899000188", "Educacional Didático Ltda", "EduDid", "SP", "São Paulo", "grande porte", "4647801"),
    ("33445566000199", "Verdeja Engenharia Ambiental S.A.", "Verdeja", "PR", "Curitiba", "EPP", "3900500"),
    ("22334455000122", "Medical Equipamentos Ltda", "MedEq", "SP", "São Bernardo do Campo", "grande porte", "4645101"),
    ("77889900000133", "InfraRede Telecom Ltda", "InfraRede", "RS", "Caxias do Sul", "grande porte", "6110801"),
]

MODALITIES = [
    ("pregao_eletronico", 1, 0.55),
    ("dispensa", 9, 0.20),
    ("inexigibilidade", 10, 0.05),
    ("concorrencia", 3, 0.10),
    ("tomada_de_precos", 4, 0.05),
    ("credenciamento", 11, 0.05),
]

CATEGORY_TEMPLATES = [
    ("Tecnologia da Informação", [
        ("Aquisição de licenças de software para gestão administrativa",
         "Contratação de empresa especializada no fornecimento de licenças de uso de software "
         "ERP para modernização dos processos administrativos do órgão, incluindo módulos de "
         "finanças, recursos humanos, compras e patrimônio, com suporte técnico 24x7 e "
         "migração de dados legados.",
         ["Licença ERP módulo financeiro", "Licença ERP módulo RH", "Suporte técnico 24x7 anual", "Treinamento de usuários"]),
        ("Contratação de serviços de computação em nuvem (IaaS/PaaS)",
         "O presente pregão eletrônico tem por objeto a contratação de serviços continuados de "
         "computação em nuvem para hospedagem de aplicações críticas do órgão, com SLA de 99.95%, "
         "backup automatizado, monitoramento 24x7 e migração assistida.",
         ["Instância computacional padrão (mês)", "Armazenamento em bloco SSD (GB/mês)", "Balanceador de carga (mês)"]),
        ("Aquisição de notebooks para servidores públicos",
         "Registro de preços para aquisição de 800 notebooks corporativos, 16GB RAM, SSD 512GB, "
         "processador Intel Core i7 ou equivalente, garantia on-site 36 meses.",
         ["Notebook corporativo i7 16GB 512GB"]),
    ]),
    ("Saúde", [
        ("Aquisição de medicamentos da farmácia básica",
         "Aquisição emergencial de medicamentos constantes da RENAME destinados ao abastecimento "
         "das unidades básicas de saúde municipais, com entrega fracionada em 12 parcelas mensais.",
         ["Dipirona 500mg comprimido", "Losartana 50mg comprimido", "Metformina 850mg comprimido", "Amoxicilina 500mg cápsula"]),
        ("Contratação de serviços de hemodiálise",
         "Contratação por credenciamento de clínicas para oferta de sessões de hemodiálise a "
         "pacientes do SUS, conforme tabela SUS/2025 e critérios técnicos do Ministério da Saúde.",
         ["Sessão de hemodiálise", "Sessão de hemodiálise de urgência"]),
        ("Aquisição de equipamentos médico-hospitalares",
         "Aquisição de respiradores, monitores multiparamétricos e bombas de infusão para "
         "reforço da rede hospitalar estadual.",
         ["Respirador UTI adulto", "Monitor multiparamétrico", "Bomba de infusão volumétrica"]),
    ]),
    ("Educação", [
        ("Aquisição de gêneros alimentícios para merenda escolar",
         "Aquisição de itens da agricultura familiar e gêneros alimentícios não perecíveis destinados "
         "à alimentação escolar das escolas municipais, conforme Lei 11.947/2009.",
         ["Arroz parboilizado 5kg", "Feijão carioca 1kg", "Leite UHT integral 1L", "Óleo de soja 900ml"]),
        ("Fornecimento de uniformes escolares",
         "Contratação de empresa para confecção e fornecimento de kits de uniformes escolares para "
         "alunos da rede pública, em conformidade com modelo padronizado.",
         ["Kit uniforme escolar fundamental", "Kit uniforme escolar médio"]),
        ("Aquisição de livros didáticos complementares",
         "Registro de preços para aquisição de livros didáticos e material pedagógico "
         "complementar destinado ao fortalecimento das ações de alfabetização.",
         ["Livro didático ciências 5º ano", "Livro didático matemática 5º ano"]),
    ]),
    ("Obras e Engenharia", [
        ("Recapeamento asfáltico de vias urbanas",
         "Contratação de empresa especializada para execução de serviços de recapeamento "
         "asfáltico, fresagem e sinalização viária em vias principais do município, incluindo "
         "drenagem superficial.",
         ["Recapeamento CBUQ 4cm m²", "Fresagem m²", "Pintura de faixa m"]),
        ("Construção de unidade básica de saúde",
         "Execução de obras civis para construção de UBS padrão do Ministério da Saúde, com 620m² "
         "de área construída, incluindo instalações, acabamentos e paisagismo.",
         ["Construção UBS padrão (serviço global)"]),
        ("Reforma de escola municipal",
         "Serviços de reforma estrutural e adequação de acessibilidade em unidade escolar, "
         "incluindo troca de cobertura, pintura, elétrica e hidráulica.",
         ["Reforma estrutural escola (serviço global)"]),
    ]),
    ("Segurança Pública", [
        ("Aquisição de coletes balísticos nível IIIA",
         "Aquisição de coletes balísticos nível IIIA com plano reforçado para operações especiais, "
         "atendendo aos padrões do Exército Brasileiro.",
         ["Colete balístico nível IIIA"]),
        ("Contratação de monitoramento eletrônico urbano",
         "Implantação e operação de sistema de monitoramento por câmeras CFTV com analítico de "
         "vídeo e integração com o centro de operações integradas.",
         ["Câmera CFTV PTZ", "Câmera fixa 4MP", "Licença analítico de vídeo"]),
    ]),
    ("Transporte e Frota", [
        ("Locação de veículos leves sem motorista",
         "Locação continuada de veículos leves de passeio sem motorista para uso administrativo, "
         "com quilometragem livre, manutenção e seguro inclusos.",
         ["Locação veículo passeio 1.0 (mês)", "Locação veículo SUV 1.5 (mês)"]),
        ("Aquisição de combustíveis para frota",
         "Registro de preços para fornecimento parcelado de gasolina comum e óleo diesel S10 para "
         "abastecimento da frota oficial.",
         ["Gasolina comum (litro)", "Óleo diesel S10 (litro)"]),
    ]),
    ("Serviços Gerais", [
        ("Contratação de serviços de limpeza e conservação",
         "Contratação continuada de mão de obra terceirizada para serviços de limpeza, higienização "
         "e conservação nas unidades administrativas, com fornecimento de todos os insumos.",
         ["Servente de limpeza (posto mensal)", "Encarregado de limpeza (posto mensal)"]),
        ("Contratação de vigilância patrimonial armada",
         "Contratação de serviços continuados de vigilância patrimonial armada 24x7, com escala "
         "12x36, em 14 postos distribuídos.",
         ["Posto vigilância armada 12x36 diurno", "Posto vigilância armada 12x36 noturno"]),
    ]),
    ("Consultoria e Assessoria", [
        ("Consultoria para modernização administrativa",
         "Contratação de consultoria especializada para elaboração de diagnóstico organizacional "
         "e plano de modernização dos processos administrativos.",
         ["Serviço de consultoria (hora técnica sênior)"]),
    ]),
    ("Materiais de Escritório", [
        ("Aquisição de materiais de escritório diversos",
         "Registro de preços para aquisição parcelada de materiais de expediente e consumíveis "
         "de escritório para unidades administrativas.",
         ["Papel A4 75g resma 500fl", "Toner laser preto", "Caneta esferográfica azul"]),
    ]),
]

STATUSES = [("published", 0.45), ("open", 0.25), ("awarded", 0.12), ("closed", 0.1), ("cancelled", 0.05), ("deserted", 0.03)]

UNITS_BY_PRODUCT = {
    "comprimido": "comprimido", "cápsula": "cápsula", "UHT": "litro",
    "kg": "quilograma", "ml": "unidade", "resma": "resma",
    "licença": "unidade", "sessão": "sessão", "m²": "m²", "m": "m",
    "litro": "litro", "mês": "mês", "posto": "posto",
    "hora": "hora", "anual": "unidade", "kit": "kit",
}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def weighted_choice(pairs: list[tuple]) -> object:
    values, weights = zip(*[(p[0] if len(p) == 2 else p[:-1], p[-1]) for p in pairs], strict=False)
    return random.choices(values, weights=weights, k=1)[0]


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def guess_unit(description: str) -> str:
    desc = description.lower()
    for key, val in UNITS_BY_PRODUCT.items():
        if key in desc:
            return val
    return "unidade"


# ----------------------------------------------------------------------------
# Builders
# ----------------------------------------------------------------------------
def build_agencies() -> list[dict]:
    return [
        {
            "cnpj": cnpj, "name": name, "short_name": short, "sphere": sphere, "branch": branch,
            "state": state, "city": city, "source": "fixture",
        }
        for (cnpj, name, short, sphere, branch, state, city) in AGENCIES
    ]


def build_suppliers() -> list[dict]:
    return [
        {
            "tax_id": tax, "tax_id_type": "CNPJ", "name": name, "trade_name": trade,
            "state": state, "city": city, "size": size, "main_cnae": cnae,
            "source": "fixture",
        }
        for (tax, name, trade, state, city, size, cnae) in SUPPLIERS
    ]


def build_opportunities() -> list[dict]:
    opps: list[dict] = []
    now = datetime(2026, 4, 15, 14, 0, 0, tzinfo=timezone.utc)

    modality_values = [(m[0], m[2]) for m in MODALITIES]

    for i in range(85):
        category, templates = random.choice(CATEGORY_TEMPLATES)
        title, body, items_stub = random.choice(templates)

        agency = random.choice(AGENCIES)
        cnpj, agency_name, short, sphere, branch, state, city = agency

        published_at = now - timedelta(days=random.randint(0, 28), hours=random.randint(0, 23))
        close_at = published_at + timedelta(days=random.randint(6, 45), hours=random.randint(0, 8))

        mod = weighted_choice(modality_values)
        status = weighted_choice(STATUSES)

        value_base = random.uniform(50_000, 12_000_000)
        if category == "Obras e Engenharia":
            value_base = random.uniform(300_000, 80_000_000)
        elif category == "Tecnologia da Informação":
            value_base = random.uniform(100_000, 15_000_000)
        elif category == "Saúde":
            value_base = random.uniform(80_000, 20_000_000)
        estimated_value = round(value_base, 2)

        sequencial = 1000 + i
        ano = 2026
        source_id = f"{cnpj}-{sequencial}-{ano}"
        control = f"{cnpj}-1-{sequencial:06d}/{ano}"

        items: list[dict] = []
        remaining = estimated_value
        n_items = len(items_stub)
        for idx, desc in enumerate(items_stub):
            last = idx == n_items - 1
            chunk = round(remaining if last else remaining * random.uniform(0.2, 0.5), 2)
            remaining = round(remaining - chunk, 2)
            qty = random.choice([50, 100, 200, 500, 1000, 5000, 12])
            unit_price = round(chunk / max(qty, 1), 2)
            # Stable CATMAT per description so pricing intelligence can aggregate.
            catmat = "BR" + str(abs(hash(desc)) % 900000 + 100000)
            items.append({
                "lot_number": 1,
                "item_number": idx + 1,
                "description": desc,
                "unit": guess_unit(desc),
                "quantity": qty,
                "unit_reference_price": unit_price,
                "total_reference_price": round(unit_price * qty, 2),
                "catmat_code": catmat,
            })

        opps.append({
            "source": "fixture",
            "source_id": source_id,
            "pncp_control_number": control,
            "notice_number": f"{i + 1:03d}/{ano}",
            "source_url": f"https://pncp.gov.br/app/editais/{control}",
            "agency_cnpj": cnpj,
            "title": title,
            "object_description": body,
            "modality": mod,
            "status": status,
            "category": category,
            "estimated_value": estimated_value,
            "currency": "BRL",
            "published_at": iso(published_at),
            "proposals_open_at": iso(published_at + timedelta(days=1)),
            "proposals_close_at": iso(close_at),
            "state": state,
            "city": city,
            "items": items,
        })
    return opps


def build_contracts(opportunities: list[dict]) -> list[dict]:
    contracts: list[dict] = []
    awarded = [o for o in opportunities if o["status"] == "awarded"]
    # Also contract a chunk of other states so we have more history
    for opp in awarded + random.sample(opportunities, k=18):
        supplier = random.choice(SUPPLIERS)
        tax, s_name, *_ = supplier
        signed_at = datetime.fromisoformat(opp["proposals_close_at"]) + timedelta(days=random.randint(5, 25))
        total = round(opp["estimated_value"] * random.uniform(0.72, 1.05), 2)
        items = [
            {
                "item_number": it["item_number"],
                "description": it["description"],
                "unit": it["unit"],
                "quantity": it["quantity"],
                "unit_price": round(it["unit_reference_price"] * random.uniform(0.70, 1.08), 2),
                "total_price": round(it["total_reference_price"] * random.uniform(0.70, 1.08), 2),
                "catmat_code": it.get("catmat_code"),
            }
            for it in opp["items"]
        ]
        contracts.append({
            "source": "fixture",
            "source_id": f"{opp['source_id']}-CT",
            "pncp_control_number": opp["pncp_control_number"] + "-CT",
            "contract_number": f"CT-{random.randint(1000, 9999)}/2026",
            "agency_cnpj": opp["agency_cnpj"],
            "supplier_tax_id": tax,
            "opportunity_source_id": opp["source_id"],
            "object_description": opp["title"] + " — contrato firmado após homologação.",
            "signed_at": iso(signed_at),
            "start_at": iso(signed_at + timedelta(days=10)),
            "end_at": iso(signed_at + timedelta(days=365)),
            "total_value": total,
            "currency": "BRL",
            "status": random.choice(["active", "active", "active", "executed", "suspended"]),
            "items": items,
        })
    return contracts


def build_pncp_snapshot(opportunities: list[dict]) -> list[dict]:
    """Repackage a subset of opportunities in PNCP-like JSON shape.

    Lets the ingestion pipeline run end-to-end against bundled fixtures
    without touching the live PNCP API.
    """
    modality_code_by_value = {m[0]: m[1] for m in MODALITIES}
    snapshot: list[dict] = []
    for opp in opportunities[:40]:
        cnpj = opp["agency_cnpj"]
        agency_row = next((a for a in AGENCIES if a[0] == cnpj), None)
        if not agency_row:
            continue
        _, a_name, a_short, a_sphere, a_branch, a_state, a_city = agency_row
        snapshot.append({
            "numeroControlePNCP": opp["pncp_control_number"],
            "numeroCompra": opp["notice_number"],
            "modalidadeId": modality_code_by_value.get(opp["modality"], 0),
            "situacaoCompraNome": "Divulgada",
            "objetoCompra": opp["title"],
            "informacaoComplementar": opp["object_description"],
            "valorTotalEstimado": opp["estimated_value"],
            "dataPublicacaoPncp": opp["published_at"],
            "dataAberturaProposta": opp["proposals_open_at"],
            "dataEncerramentoProposta": opp["proposals_close_at"],
            "linkSistemaOrigem": opp["source_url"],
            "orgaoEntidade": {
                "cnpj": cnpj, "razaoSocial": a_name, "nomeFantasia": a_short,
                "esferaId": a_sphere, "poderId": a_branch,
            },
            "unidadeOrgao": {
                "ufSigla": a_state, "municipioNome": a_city, "codigoIbge": None,
            },
            "itens": [
                {
                    "numeroItem": it["item_number"],
                    "numeroLote": it.get("lot_number"),
                    "descricao": it["description"],
                    "unidadeMedida": it["unit"],
                    "quantidade": it["quantity"],
                    "valorUnitarioEstimado": it["unit_reference_price"],
                    "valorTotal": it["total_reference_price"],
                    "codigoItemCatalogo": it.get("catmat_code"),
                }
                for it in opp["items"]
            ],
        })
    return snapshot


def main() -> None:
    agencies = build_agencies()
    suppliers = build_suppliers()
    opportunities = build_opportunities()
    contracts = build_contracts(opportunities)
    pncp_snapshot = build_pncp_snapshot(opportunities)

    def dump(name: str, data) -> None:
        path = OUT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"wrote {path}  ({len(data)} records)")

    dump("agencies.json", agencies)
    dump("suppliers.json", suppliers)
    dump("opportunities.json", opportunities)
    dump("contracts.json", contracts)
    dump("pncp/opportunities.json", pncp_snapshot)


if __name__ == "__main__":
    main()
