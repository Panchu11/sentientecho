"""
Logging configuration for SentientEcho.
"""

import logging
import sys
from typing import Optional

try:
    import structlog
    from ..config import get_settings
    STRUCTLOG_AVAILABLE = True
except ImportError:
    # For direct execution/testing
    STRUCTLOG_AVAILABLE = False
    try:
        from config import get_settings
    except ImportError:
        get_settings = None


def configure_logging():
    """Configure structured logging for the application."""
    if STRUCTLOG_AVAILABLE and get_settings:
        settings = get_settings()

        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, settings.log_level.upper(), logging.INFO),
        )
    else:
        # Fallback to basic logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
            level=logging.INFO,
        )


def get_logger(name: Optional[str] = None):
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name or __name__)


# Configure logging on import
configure_logging()
