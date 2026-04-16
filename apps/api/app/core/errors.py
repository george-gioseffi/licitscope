"""Uniform JSON error responses.

Every unhandled exception, every HTTPException, and every Pydantic
validation error gets mapped to the same JSON envelope:

    {
      "error": "<human message>",
      "type":  "<stable machine code>",
      "request_id": "<correlation id>",
      "details": <optional structured payload>
    }

This makes the API consistent for clients and keeps internal tracebacks
out of production responses.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _envelope(
    *,
    message: str,
    error_type: str,
    status_code: int,
    request: Request,
    details: object | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    body: dict[str, object] = {
        "error": message,
        "type": error_type,
        "request_id": request_id,
    }
    if details is not None:
        body["details"] = details
    headers = {"x-request-id": request_id} if request_id else None
    return JSONResponse(status_code=status_code, content=body, headers=headers)


def install_exception_handlers(app: FastAPI) -> None:
    """Attach the three handlers to a FastAPI app."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return _envelope(
            message=exc.detail if isinstance(exc.detail, str) else "http_error",
            error_type=f"http_{exc.status_code}",
            status_code=exc.status_code,
            request=request,
            details=None if isinstance(exc.detail, str) else jsonable_encoder(exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return _envelope(
            message="Request failed validation.",
            error_type="validation_error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            request=request,
            details=jsonable_encoder(exc.errors()),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _envelope(
            message="Internal server error.",
            error_type="internal_error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request=request,
            details=None,
        )
