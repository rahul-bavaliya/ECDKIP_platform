import logging
import sys

import structlog
from asgi_correlation_id.context import correlation_id


def setup_logging(is_production: bool = False):
    # 1. Choose log level based on environment
    log_level = logging.INFO if is_production else logging.DEBUG

    # 2. Define the processing pipeline
    processors = [
        # Merges external logging context into structlog
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        # Dynamically injects Request/Correlation ID from ASGI middleware
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,  # Formats tracebacks cleanly
        structlog.processors.UnicodeDecoder(),
    ]

    if is_production:
        # In Production: Output purely machine-readable JSON
        processors.append(structlog.processors.JSONRenderer())
    else:
        # In Development: Use beautiful, color-coded human-readable console blocks
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # 3. Apply settings natively to python's base logging infrastructure
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    structlog.configure(
        processors=[
            # Inject context variables (like the correlation ID) globally
            structlog.contextvars.merge_contextvars,
            *processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger() -> structlog.BoundLogger:
    """Injects or fetches the contextual logger instance."""
    # Instantly bind the dynamic Correlation ID if it exists in the execution context
    req_id = correlation_id.get()
    return (
        structlog.get_logger().bind(request_id=req_id)
        if req_id
        else structlog.get_logger()
    )
