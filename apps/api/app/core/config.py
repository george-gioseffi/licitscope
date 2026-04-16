"""Application settings, loaded from environment variables (pydantic-settings)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    """Runtime configuration for the API."""

    model_config = SettingsConfigDict(
        env_file=(".env", str(REPO_ROOT / ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- app ---------------------------------------------------------------
    app_env: str = "development"
    app_name: str = "LicitScope"
    app_log_level: str = "INFO"

    # --- api ---------------------------------------------------------------
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- database ----------------------------------------------------------
    database_url: str = "sqlite:///./licitscope.db"

    # --- ingestion ---------------------------------------------------------
    pncp_base_url: str = "https://pncp.gov.br/api/consulta"
    ingestion_use_fixtures: bool = True
    ingestion_page_size: int = 50
    ingestion_max_pages: int = 5
    ingestion_request_timeout: int = 30

    # --- enrichment --------------------------------------------------------
    enrichment_mode: str = "offline"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    # --- demo / fixtures ---------------------------------------------------
    data_demo_dir: Path = REPO_ROOT / "data-demo"

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # convenient flags
    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgres")


@lru_cache
def get_settings() -> Settings:
    return Settings()
