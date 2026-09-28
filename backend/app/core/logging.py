import sys
from app.core.config import settings

try:
    from loguru import logger
except ImportError:
    import logging

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
    )
    logger = logging.getLogger("docuagent")



def setup_logging():
    """Configure loguru structured logging handler."""
    if hasattr(logger, "remove"):
        logger.remove()
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.LOG_LEVEL,
        )
    logger.info(f"Initialized logger with level {settings.LOG_LEVEL}")



__all__ = ["logger", "setup_logging"]
