"""
Central logger configuration for the application.
Import `logger` from here.
"""

import logging
import sys
from typing import List, Optional
from loguru import logger

from src.config.params import DEBUG_LOGS

DEPENDENCIES_WITH_LOGGING: List[str] = []

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def disable_dependency_loggers(dependencies: List[str]) -> None:
    """
    Disables the passed dependencies from Python's default logging library

    Parameters
    ----------
    dependencies: List[str]
        The list of dependencies to disable from Python's default logging library
    """
    for name in dependencies:
        logging.getLogger(name).disabled = True
        logging.getLogger(name).propagate = False


def setup_logger(debug: Optional[bool] = None) -> None:
    logger.remove()

    # Determine the "Floor" level (DEBUG or INFO)
    base_level = "DEBUG" if debug else "INFO"

    # 1. Console: Standard Output (DEBUG/INFO)
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=base_level,
        filter=lambda r: r["level"].no < 30, # Stop before WARNING
    )

    # 2. Console: Standard Error (WARNING+)
    logger.add(
        sys.stderr,
        format="\n" + LOG_FORMAT,
        level="WARNING",
    )

    # 3. File: Persistent storage (Matches base_level)
    logger.add(
        "data/logs/app.log",  # "app_{time:YYYY-MM-DD}.log",
        format=LOG_FORMAT,
        level=base_level,  # <--- Now it respects the debug toggle!
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True
    )


# Run once when module is imported
disable_dependency_loggers(DEPENDENCIES_WITH_LOGGING)
setup_logger(debug=DEBUG_LOGS)
