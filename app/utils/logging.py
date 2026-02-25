"""
Structured logging configuration using structlog.
@SPEC:IMPROVE-001 REQ-LOG-001, REQ-LOG-002, REQ-LOG-003
"""

import logging
import sys
import structlog
from typing import Optional
from flask import request, g
import time
import uuid


def configure_logging(log_level: str = 'INFO', log_format: str = 'json') -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' or 'console')
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        add_request_context,
    ]

    if log_format == 'console':
        # Human-readable console output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=level,
    )

    # Set Flask's default logger to use our configuration
    flask_logger = logging.getLogger('flask')
    flask_logger.setLevel(level)


def add_request_context(logger, method_name, event_dict):
    """
    Add request context to log entries.
    @SPEC:IMPROVE-001 REQ-LOG-003
    """
    try:
        # Add request ID if available
        if hasattr(g, 'request_id'):
            event_dict['request_id'] = g.request_id

        # Add request info if in request context
        if request:
            event_dict['method'] = request.method
            event_dict['path'] = request.path
            event_dict['remote_addr'] = request.remote_addr

            # Add response time if available
            if hasattr(g, 'start_time'):
                event_dict['response_time_ms'] = round(
                    (time.time() - g.start_time) * 1000, 2
                )
    except RuntimeError:
        # Not in request context
        pass

    return event_dict


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name, typically __name__

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class RequestLogger:
    """
    Context manager for request logging.
    Logs request start, end, and duration.
    """

    def __init__(self, logger: Optional[structlog.stdlib.BoundLogger] = None):
        self.logger = logger or get_logger(__name__)

    def __enter__(self):
        """Log request start and set up timing."""
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]

        self.logger.info(
            "Request started",
            request_id=g.request_id,
            method=request.method,
            path=request.path,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Log request completion."""
        duration_ms = round((time.time() - g.start_time) * 1000, 2)

        if exc_type:
            self.logger.error(
                "Request failed",
                request_id=g.request_id,
                duration_ms=duration_ms,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
            )
        else:
            self.logger.info(
                "Request completed",
                request_id=g.request_id,
                duration_ms=duration_ms,
            )

        return False  # Don't suppress exceptions
