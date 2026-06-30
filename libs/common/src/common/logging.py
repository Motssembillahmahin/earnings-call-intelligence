"""Structured JSON logging configured once per process."""

import json
import logging
import sys

_CONFIGURED = False

_RESERVED = set(logging.makeLogRecord({}).__dict__.keys()) | {"message", "asctime", "taskName"}


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _configure() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    from .settings import get_settings

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(get_settings().log_level.upper())
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger backed by the shared JSON handler."""
    _configure()
    return logging.getLogger(name)
