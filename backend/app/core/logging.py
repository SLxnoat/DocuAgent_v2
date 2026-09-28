"""Structured logging configuration using Loguru."""

import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure loguru structured logging handler."""
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
    )
    logger.info(f"Initialized logger with level {settings.LOG_LEVEL}")


__all__ = ["logger", "setup_logging"]
