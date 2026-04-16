"""Domain enumerations.

We use plain ``str, Enum`` instead of SQLAlchemy Enum column types so the
schema stays portable between SQLite and Postgres without custom migrations.
"""

from __future__ import annotations

from enum import Enum


class SourceName(str, Enum):
    """Origin of a record."""

    PNCP = "pncp"
    PORTAL_TRANSPARENCIA = "portal_transparencia"
    COMPRAS_GOV_BR = "compras_gov_br"
    FIXTURE = "fixture"


class ModalityCode(str, Enum):
    """Procurement modality. Codes follow the Lei 14.133/2021 taxonomy."""

    PREGAO_ELETRONICO = "pregao_eletronico"
    PREGAO_PRESENCIAL = "pregao_presencial"
    CONCORRENCIA = "concorrencia"
    TOMADA_DE_PRECOS = "tomada_de_precos"
    CONVITE = "convite"
    CONCURSO = "concurso"
    LEILAO = "leilao"
    DIALOGO_COMPETITIVO = "dialogo_competitivo"
    DISPENSA = "dispensa"
    INEXIGIBILIDADE = "inexigibilidade"
    CREDENCIAMENTO = "credenciamento"
    OUTROS = "outros"


MODALITY_LABELS: dict[str, str] = {
    ModalityCode.PREGAO_ELETRONICO.value: "Pregão Eletrônico",
    ModalityCode.PREGAO_PRESENCIAL.value: "Pregão Presencial",
    ModalityCode.CONCORRENCIA.value: "Concorrência",
    ModalityCode.TOMADA_DE_PRECOS.value: "Tomada de Preços",
    ModalityCode.CONVITE.value: "Convite",
    ModalityCode.CONCURSO.value: "Concurso",
    ModalityCode.LEILAO.value: "Leilão",
    ModalityCode.DIALOGO_COMPETITIVO.value: "Diálogo Competitivo",
    ModalityCode.DISPENSA.value: "Dispensa de Licitação",
    ModalityCode.INEXIGIBILIDADE.value: "Inexigibilidade",
    ModalityCode.CREDENCIAMENTO.value: "Credenciamento",
    ModalityCode.OUTROS.value: "Outros",
}


class OpportunityStatus(str, Enum):
    """Lifecycle of a procurement notice."""

    DRAFT = "draft"
    PUBLISHED = "published"
    OPEN = "open"
    PROPOSALS_RECEIVED = "proposals_received"
    UNDER_ANALYSIS = "under_analysis"
    AWARDED = "awarded"
    CONTRACTED = "contracted"
    CANCELLED = "cancelled"
    DESERTED = "deserted"
    CLOSED = "closed"


class IngestionStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    RUNNING = "running"
