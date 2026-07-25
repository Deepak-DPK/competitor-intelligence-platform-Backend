"""
app/core/logging.py
-------------------
Configures structured, JSON-capable logging for the application.

Usage:
    from app.core.logging import setup_logging, get_logger

    setup_logging()  # called once at startup in main.py
    logger = get_logger(__name__)
    logger.info("Something happened", extra={"user_id": "abc"})
"""

import logging
import sys
from typing import Optional

from app.core.config import settings


# ------------------------------------------------------------------ #
# JSON formatter (lightweight — no third-party dependency)
# ------------------------------------------------------------------ #
import json
import traceback
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Emits every log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        log_data: dict = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "environment": settings.ENVIRONMENT,
            "app": settings.APP_NAME,
        }

        # Thread / task context
        if record.thread:
            log_data["thread"] = record.thread

        # Extra fields injected via `extra={...}` in logger calls
        for key, value in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text",
                "filename", "funcName", "id", "levelname", "levelno",
                "lineno", "module", "msecs", "message", "msg", "name",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "thread", "threadName",
            ):
                log_data[key] = value

        # Exception info
        if record.exc_info:
            log_data["exception"] = traceback.format_exception(*record.exc_info)

        return json.dumps(log_data, default=str)


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #

def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure root logger.  Call this exactly once at application startup.

    In development we use a human-readable format; in production we emit JSON.
    """
    log_level_str = level or settings.LOG_LEVEL
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicate logs
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if settings.is_production:
        handler.setFormatter(JsonFormatter())
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger.addHandler(handler)

    # Quieten noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.  Always prefer this over ``logging.getLogger`` directly."""
    return logging.getLogger(name)
