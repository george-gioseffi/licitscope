"""HTTP middleware — request id propagation and access logging.

Each inbound request is tagged with an ``X-Request-ID`` (honoring a
client-supplied one if present, otherwise generating a ULID-ish UUID).
The id is echoed back on the response and logged with the status code
and duration, so any operator reading the logs can correlate a single
request across the whole stack.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("licitscope.access")

_REQUEST_ID_HEADER = "x-request-id"


async def request_context_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get(_REQUEST_ID_HEADER) or uuid.uuid4().hex
    request.state.request_id = request_id

    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.exception(
            "request %s %s FAILED after %.1fms (request_id=%s)",
            request.method,
            request.url.path,
            elapsed_ms,
            request_id,
        )
        raise
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers[_REQUEST_ID_HEADER] = request_id

    # Skip access log for the liveness probe — it'd drown real traffic.
    if request.url.path != "/health/live":
        logger.info(
            "%s %s -> %s in %.1fms (request_id=%s)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )
    return response
