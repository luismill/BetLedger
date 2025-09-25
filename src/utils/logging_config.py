"""Structured logging configuration."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "betledger.log"


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=3)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if not any(isinstance(h, RotatingFileHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(file=handler.stream),
    )
