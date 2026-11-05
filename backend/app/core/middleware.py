import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.core.responses import error_response

logger = logging.getLogger("app.request")


def register_middleware(app: FastAPI, settings: Settings) -> None:
    @app.middleware("http")
    async def request_context(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = uuid4().hex[:8]
        started = perf_counter()

        # Unexpected errors are caught here, not in an Exception handler: those
        # run outside CORSMiddleware, so the browser would hide the 500 body.
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("[%s] unhandled error", request_id)
            response = error_response(500, "internal_error", "Something went wrong")

        duration_ms = (perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms:.1f}ms"
        logger.info(
            "[%s] %s %s -> %s (%.1fms)",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    # Added last so it is the outermost layer and also covers the 500 above.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )
