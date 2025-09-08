"""
Logging configuration
"""
import sys
from loguru import logger
from config.settings import LOG_LEVEL, LOG_FILE


def setup_logger():
    """Setup logger configuration"""
    print(f"--- LOGGER SETUP: Initializing logger with LOG_LEVEL = '{LOG_LEVEL}' ---")
    # Remove default logger
    logger.remove()

    # Add console logger
    logger.add(
        sys.stdout,
        level=LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )

    # Add file logger
    logger.add(
        LOG_FILE,
        level=LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )

    return logger


# Initialize logger
log = setup_logger()
