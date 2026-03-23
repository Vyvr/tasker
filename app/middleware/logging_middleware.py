import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

error_logger = logging.getLogger("app.error")
warning_logger = logging.getLogger("app.warning")
request_logger = logging.getLogger("app.request")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            error_logger.error(
                "Unhandled exception | %s %s | %s: %s",
                request.method,
                request.url.path,
                type(exc).__name__,
                exc,
            )
            raise

        duration_ms = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code

        log_line = "%s %s | %d | %.1fms" % (
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )

        if status_code >= 500:
            error_logger.error(log_line)
        elif status_code >= 400:
            warning_logger.warning(log_line)
        else:
            request_logger.info(log_line)

        return response
