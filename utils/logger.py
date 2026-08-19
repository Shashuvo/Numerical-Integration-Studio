"""
Centralized logging configuration for Numerical Integration Studio.

All modules should obtain their logger via ``get_logger(__name__)``
rather than calling ``logging.getLogger`` directly, so log format,
level, and handlers stay consistent across the whole application.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path("logs")
_LOG_FILE = _LOG_DIR / "nis.log"
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the root application logger.

    Sets up both a rotating file handler (for persistent diagnostics)
    and a console handler (for immediate developer feedback). Safe to
    call multiple times; configuration is only applied once.

    Args:
        level: The minimum logging level to capture (e.g. logging.DEBUG).
    """
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger("nis")
    root_logger.setLevel(level)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = RotatingFileHandler(
        _LOG_FILE, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.propagate = False

    _configured = True


def get_logger(module_name: str) -> logging.Logger:
    """Return a namespaced logger for the given module.

    Args:
        module_name: Typically ``__name__`` of the calling module.

    Returns:
        A ``logging.Logger`` instance scoped under the ``nis`` namespace.
    """
    if not _configured:
        configure_logging()
    return logging.getLogger(f"nis.{module_name}")
