"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.routers import (
    agencies,
    analytics,
    contracts,
    health,
    meta,
    opportunities,
    search,
    suppliers,
    watchlists,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    init_db()
    logger.info("LicitScope API %s started in %s mode", __version__, get_settings().app_env)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="LicitScope API",
        description=(
            "AI-powered procurement intelligence for Brazilian public "
            "procurement data. This API serves normalized data from PNCP "
            "and related sources, plus AI-enriched insights."
        ),
        version=__version__,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # routers
    app.include_router(health.router)
    app.include_router(meta.router)
    app.include_router(opportunities.router)
    app.include_router(search.router)
    app.include_router(agencies.router)
    app.include_router(suppliers.router)
    app.include_router(contracts.router)
    app.include_router(analytics.router)
    app.include_router(watchlists.router)

    @app.get("/", tags=["meta"], include_in_schema=False)
    def root() -> JSONResponse:
        return JSONResponse(
            {
                "name": settings.app_name,
                "version": __version__,
                "docs": "/docs",
                "health": "/health/ready",
            }
        )

    return app


app = create_app()
