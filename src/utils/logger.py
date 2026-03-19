"""
Logging configuration with optional loguru support.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from config.settings import LOG_LEVEL, LOG_FILE

try:
    from loguru import logger as _loguru_logger
except ModuleNotFoundError:
    _loguru_logger = None


def _resolve_log_level() -> int:
    return getattr(logging, LOG_LEVEL.upper(), logging.INFO)


class _StdlibLoggerAdapter:
    """
    Small compatibility wrapper to mimic the subset of loguru used by the codebase.
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def __getattr__(self, name: str) -> Any:
        return getattr(self._logger, name)

    def success(self, message: str, *args, **kwargs) -> None:
        self._logger.info(message, *args, **kwargs)

    def trace(self, message: str, *args, **kwargs) -> None:
        self._logger.debug(message, *args, **kwargs)


def _setup_loguru_logger():
    """Configure loguru when the dependency is available."""
    _loguru_logger.remove()

    _loguru_logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    _loguru_logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        rotation="10 MB",
        retention="7 days",
        compression="zip",
    )

    return _loguru_logger


def _setup_stdlib_logger() -> _StdlibLoggerAdapter:
    """Configure stdlib logging as a fallback when loguru is unavailable."""
    log_level = _resolve_log_level()
    logger = logging.getLogger("uni_bot")
    logger.setLevel(log_level)
    logger.propagate = False

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as exc:
        logger.warning(f"Could not initialize file logger at '{LOG_FILE}': {exc}")

    adapter = _StdlibLoggerAdapter(logger)
    adapter.warning("loguru is not installed; falling back to Python logging")
    return adapter


def setup_logger():
    """Setup logger configuration with loguru when available, stdlib otherwise."""
    if _loguru_logger is not None:
        return _setup_loguru_logger()
    return _setup_stdlib_logger()


log = setup_logger()
