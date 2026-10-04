"""Structured logging configuration."""

import logging
import sys
from contextvars import ContextVar

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


class StructuredFormatter(logging.Formatter):
    """Formatter that injects contextual information like request_id."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_ctx_var.get()
        record.request_id = req_id if req_id else "-"
        return super().format(record)


def configure_logging(level_name: str = "INFO") -> None:
    """Configure root logger with structured format."""
    log_level = getattr(logging, level_name.upper(), logging.INFO)

    log_format = (
        "%(asctime)s | %(levelname)-7s | [%(request_id)s] | %(name)s:%(lineno)d | %(message)s"
    )
    formatter = StructuredFormatter(log_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
