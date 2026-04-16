"""Translate PNCP JSON payloads into LicitScope's normalized shape.

Real PNCP payloads are verbose and nested; this module keeps the mapping in
one place and is the single source of truth for ingestion normalization.
The return value is a tuple ``(agency_payload, opportunity_payload, items)``
ready to feed into :class:`~app.repositories.opportunities.OpportunityRepository`.
"""

from __future__ import annotations

from typing import Any

from app.models.enums import ModalityCode, OpportunityStatus, SourceName
from app.utils.dates import parse_date
from app.utils.money import parse_brl

# PNCP numeric modality codes → our enum values.
MODALITY_BY_CODE: dict[int, str] = {
    1: ModalityCode.PREGAO_ELETRONICO.value,
    2: ModalityCode.PREGAO_PRESENCIAL.value,
    3: ModalityCode.CONCORRENCIA.value,
    4: ModalityCode.TOMADA_DE_PRECOS.value,
    5: ModalityCode.CONVITE.value,
    6: ModalityCode.CONCURSO.value,
    7: ModalityCode.LEILAO.value,
    8: ModalityCode.DIALOGO_COMPETITIVO.value,
    9: ModalityCode.DISPENSA.value,
    10: ModalityCode.INEXIGIBILIDADE.value,
    11: ModalityCode.CREDENCIAMENTO.value,
}

# Descriptive PNCP status strings → our enum values.
STATUS_MAP: dict[str, str] = {
    "divulgada": OpportunityStatus.PUBLISHED.value,
    "divulgado": OpportunityStatus.PUBLISHED.value,
    "publicada": OpportunityStatus.PUBLISHED.value,
    "aberta": OpportunityStatus.OPEN.value,
    "em andamento": OpportunityStatus.OPEN.value,
    "encerrada": OpportunityStatus.CLOSED.value,
    "homologada": OpportunityStatus.AWARDED.value,
    "adjudicada": OpportunityStatus.AWARDED.value,
    "cancelada": OpportunityStatus.CANCELLED.value,
    "revogada": OpportunityStatus.CANCELLED.value,
    "deserta": OpportunityStatus.DESERTED.value,
}


def _get(d: dict, *keys: str, default: Any = None) -> Any:
    """Return the first non-None value among the listed keys."""
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def parse_agency(payload: dict) -> dict:
    """Extract the órgão (agency) portion of a PNCP notice payload."""
    orgao = payload.get("orgaoEntidade") or payload.get("orgao") or {}
    unidade = payload.get("unidadeOrgao") or {}
    cnpj = _clean_str(orgao.get("cnpj") or payload.get("cnpjOrgao")) or "UNKNOWN"
    state = _clean_str(_get(unidade, "ufSigla", "uf", default=payload.get("ufSigla")))
    return {
        "cnpj": cnpj,
        "name": _clean_str(_get(orgao, "razaoSocial", "nome", default=payload.get("nomeOrgao")))
        or "Órgão desconhecido",
        "short_name": _clean_str(orgao.get("nomeFantasia")),
        "sphere": _clean_str(orgao.get("esferaId") or orgao.get("poderId")),
        "branch": _clean_str(orgao.get("poderId")),
        "state": state.upper()[:2] if state else None,
        "city": _clean_str(
            _get(unidade, "municipioNome", "nomeMunicipio", default=payload.get("nomeMunicipio"))
        ),
        "ibge_code": _clean_str(unidade.get("codigoIbge")),
        "source": SourceName.PNCP.value,
    }


def parse_opportunity(payload: dict) -> dict:
    """Normalize a PNCP notice into an Opportunity row."""
    modality_code = payload.get("modalidadeId") or payload.get("codigoModalidadeContratacao")
    try:
        modality = MODALITY_BY_CODE.get(int(modality_code), ModalityCode.OUTROS.value)
    except (TypeError, ValueError):
        modality = ModalityCode.OUTROS.value

    raw_status = (
        str(payload.get("situacaoCompraNome") or payload.get("situacao") or "").lower().strip()
    )
    status = STATUS_MAP.get(raw_status, OpportunityStatus.PUBLISHED.value)

    source_id = (
        _clean_str(
            payload.get("numeroControlePNCP") or payload.get("numeroCompra") or payload.get("id")
        )
        or ""
    )

    unidade = payload.get("unidadeOrgao") or {}
    state = _clean_str(_get(unidade, "ufSigla") or payload.get("ufSigla"))

    return {
        "source": SourceName.PNCP.value,
        "source_id": source_id,
        "source_url": _clean_str(payload.get("linkSistemaOrigem")),
        "pncp_control_number": _clean_str(payload.get("numeroControlePNCP")),
        "notice_number": _clean_str(payload.get("numeroCompra") or payload.get("numeroAno")),
        "title": (_clean_str(_get(payload, "objetoCompra", "descricao")) or "Licitação sem título"),
        "object_description": _get(
            payload,
            "informacaoComplementar",
            "objetoCompra",
            "descricaoCompleta",
            default="",
        )
        or "",
        "modality": modality,
        "status": status,
        "category": None,
        "estimated_value": parse_brl(
            _get(payload, "valorTotalEstimado", "valorTotal", "valorEstimadoTotal")
        ),
        "currency": "BRL",
        "published_at": parse_date(
            _get(payload, "dataPublicacaoPncp", "dataDivulgacaoPncp", "dataPublicacao")
        ),
        "proposals_open_at": parse_date(payload.get("dataAberturaProposta")),
        "proposals_close_at": parse_date(payload.get("dataEncerramentoProposta")),
        "session_at": parse_date(payload.get("dataInicioVigencia") or payload.get("dataSessao")),
        "state": state.upper()[:2] if state else None,
        "city": _clean_str(_get(unidade, "municipioNome") or payload.get("nomeMunicipio")),
        "raw_metadata": payload,
    }


def parse_items(payload: dict) -> list[dict]:
    """Extract item rows from a PNCP notice payload."""
    items = payload.get("itens") or payload.get("items") or []
    normalized: list[dict] = []
    for idx, it in enumerate(items, start=1):
        normalized.append(
            {
                "lot_number": it.get("numeroLote"),
                "item_number": it.get("numeroItem") or idx,
                "description": _get(it, "descricao", "descricaoItem", default=f"Item {idx}"),
                "unit": _get(it, "unidadeMedida", "unidade"),
                "quantity": parse_brl(it.get("quantidade")),
                "unit_reference_price": parse_brl(it.get("valorUnitarioEstimado")),
                "total_reference_price": parse_brl(it.get("valorTotal")),
                "catmat_code": str(it.get("codigoItemCatalogo") or it.get("catmat") or "") or None,
                "catser_code": str(it.get("catser") or "") or None,
            }
        )
    return normalized


def parse_full(payload: dict) -> tuple[dict, dict, list[dict]]:
    return parse_agency(payload), parse_opportunity(payload), parse_items(payload)
