"""
Custom middleware for request/response processing.

This module provides middleware for logging, timing, and other
cross-cutting concerns.
"""

import time

import structlog
from asgi_correlation_id import correlation_id
from fastapi import Request, Response
from uvicorn.protocols.utils import get_path_with_query_string

access_logger = structlog.stdlib.get_logger('api.access')


async def logging_middleware(request: Request, call_next) -> Response:
    """
    Log all HTTP requests with timing and context information.

    This middleware logs request details including method, URL, status code,
    and processing time. It also binds the correlation ID to the log context.

    Args:
        request: The incoming HTTP request
        call_next: The next middleware or route handler

    Returns:
        HTTP response with added timing headers

    Example:
        >>> app.middleware('http')(logging_middleware)
    """
    structlog.contextvars.clear_contextvars()

    request_id = correlation_id.get()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    start_time = time.perf_counter_ns()
    response = Response(status_code=500)
    try:
        response = await call_next(request)
    except Exception:
        structlog.stdlib.get_logger('api.error').exception(
            'Uncaught exception'
        )
        raise

    process_time = time.perf_counter_ns() - start_time
    status_code = response.status_code
    url = get_path_with_query_string(request.scope)
    client_host = request.client.host
    client_port = request.client.port
    http_method = request.method
    http_version = request.scope['http_version']

    access_logger.info(
        f'{client_host}:{client_port} - "{http_method} {url} '
        f'HTTP/{http_version}" {status_code} '
        f'{process_time / 1_000_000:.2f}ms',
        http={
            'url': url,
            'status_code': status_code,
            'method': http_method,
            'request_id': request_id,
            'version': http_version,
        },
        network={'client': {'ip': client_host, 'port': client_port}},
        duration=f'{process_time / 1_000_000:.2f}ms',
    )
    response.headers['X-Process-Time'] = str(process_time / 1_000_000_000)

    return response
