"""Catalog + metadata endpoints — enumerations the frontend needs."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.enums import MODALITY_LABELS, ModalityCode, OpportunityStatus, SourceName

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/modalities")
def modalities() -> list[dict]:
    return [
        {"value": m.value, "label": MODALITY_LABELS.get(m.value, m.value)} for m in ModalityCode
    ]


@router.get("/statuses")
def statuses() -> list[dict]:
    return [
        {"value": s.value, "label": s.value.replace("_", " ").title()} for s in OpportunityStatus
    ]


@router.get("/sources")
def sources() -> list[dict]:
    labels = {
        SourceName.PNCP.value: "Portal Nacional de Contratações Públicas",
        SourceName.PORTAL_TRANSPARENCIA.value: "Portal da Transparência",
        SourceName.COMPRAS_GOV_BR.value: "Compras.gov.br",
        SourceName.FIXTURE.value: "Demo fixtures",
    }
    return [{"value": s.value, "label": labels[s.value]} for s in SourceName]
