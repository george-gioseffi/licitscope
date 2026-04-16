"""SQLModel-based ORM models for LicitScope.

Importing this package imports every concrete model, so SQLModel.metadata
contains the full schema by the time ``init_db()`` runs.
"""

from app.models.agency import Agency
from app.models.contract import Contract, ContractItem
from app.models.enrichment import Enrichment
from app.models.enums import (
    IngestionStatus,
    ModalityCode,
    OpportunityStatus,
    SourceName,
)
from app.models.ingestion import IngestionRun, RawPayload
from app.models.opportunity import Opportunity, OpportunityItem
from app.models.supplier import Supplier
from app.models.watchlist import Alert, Watchlist

__all__ = [
    "Agency",
    "Alert",
    "Contract",
    "ContractItem",
    "Enrichment",
    "IngestionRun",
    "IngestionStatus",
    "ModalityCode",
    "Opportunity",
    "OpportunityItem",
    "OpportunityStatus",
    "RawPayload",
    "SourceName",
    "Supplier",
    "Watchlist",
]
