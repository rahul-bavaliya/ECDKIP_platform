import time

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import router as api_v1_router
from app.core import get_logger, setup_logging
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)

# Initialize enterprise structured logs (True = JSON, False = Color Dev Console)
setup_logging(is_production=False)
logger = get_logger()

app = FastAPI(
    title="Enterprise Cloud Document & Knowledge Intelligence Platform",
    description="Multi-tenant RAG and document intelligence backend powered by FastAPI and PostgreSQL.",
    version="0.1.0",
)

# Global Cross-Origin Resource Sharing (CORS) Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tracing System: Inject a distinct request UUID to connect logs over asynchronous threads
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
)

# Mount central API routing structure wrapped with standard /api/v1 prefixing
app.include_router(api_v1_router, prefix="/api/v1")


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Global request lifecycle interceptor providing execution telemetry."""
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        path=request.url.path,
        method=request.method,
    )

    start_time = time.perf_counter()
    logger.info("Incoming HTTP Request")

    try:
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000

        logger.info(
            "HTTP Request Completed",
            status_code=response.status_code,
            duration_ms=f"{process_time:.2f}",
        )
        return response
    except Exception as e:
        process_time = (time.perf_counter() - start_time) * 1000
        logger.error(
            "HTTP Request Failed Exception Raised",
            error=str(e),
            duration_ms=f"{process_time:.2f}",
        )
        raise e


"""Adding the Exception Handling"""


# Register Global Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
