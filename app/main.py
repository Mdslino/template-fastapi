import logging
import time
from logging.config import dictConfig

import structlog
from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import Depends, FastAPI, Request, Response
from fastapi.logger import logger as fastapi_logger
from sqlalchemy import text
from sqlalchemy.orm import Session
from uvicorn.protocols.utils import get_path_with_query_string

from app.core.config import settings
from app.core.deps import get_db, UserDep
from app.core.endpoints import router
from app.custom_logging import setup_logging

logger = structlog.get_logger(__name__)

setup_logging(json_logs=settings.JSON_LOGS, log_level=settings.LOG_LEVEL)
access_logger = structlog.stdlib.get_logger('api.access')


def create_app():
    dictConfig(settings.LOGGING_CONFIG)
    fastapi_app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    fastapi_app.include_router(router, prefix=settings.API_V1_STR)

    @fastapi_app.get('/healthcheck')
    def healthcheck(db: Session = Depends(get_db)):
        db_status = 'ok'
        try:
            db.execute(text('SELECT 1'))
        except Exception as e:
            db_status = 'error'
            logger.error('Database is not available', exc_info=e)

        return {'app': 'ok', 'db': db_status, 'version': settings.APP_VERSION}

    @fastapi_app.get('/auth-healthcheck')
    def auth_healthcheck(user: UserDep):
        return user

    return fastapi_app


app = create_app()


@app.middleware('http')
async def logging_middleware(request: Request, call_next) -> Response:
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
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code
        url = get_path_with_query_string(request.scope)
        client_host = request.client.host
        client_port = request.client.port
        http_method = request.method
        http_version = request.scope['http_version']

        access_logger.info(
            f"""{client_host}:{client_port} - "{http_method} {url} HTTP/{http_version}" {status_code} {process_time / 1_000_000:.2f}ms""",
            http={
                'url': url,
                'status_code': status_code,
                'method': http_method,
                'request_id': request_id,
                'version': http_version,
            },
            network={'client': {'ip': client_host, 'port': client_port}},
            duration=process_time,
        )
        response.headers['X-Process-Time'] = str(process_time / 1_000_000_000)

        return response


app.add_middleware(CorrelationIdMiddleware)

if __name__ == '__main__':  # pragma: no cover
    # This is only for local development.
    import uvicorn

    fastapi_logger.setLevel(logger.level)
    app = create_app()
    uvicorn.run(app, host='0.0.0.0', port=8000)
else:
    fastapi_logger.setLevel(logging.DEBUG)
