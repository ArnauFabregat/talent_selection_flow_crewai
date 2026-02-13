"""
Central logger configuration for the application.
Import `logger` from here.
"""

import logging
import sys
from typing import List
from loguru import logger

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


def setup_logger() -> None:
    """Configure Loguru."""
    logger.remove()

    # Only DEBUG and INFO to stdout
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="DEBUG",
        filter=lambda r: r["level"].no < logger.level("WARNING").no,
    )

    # WARNING and above to stderr
    logger.add(
        sys.stderr,
        format="\n" + LOG_FORMAT,
        level="WARNING",
    )


# Run once when module is imported
disable_dependency_loggers(DEPENDENCIES_WITH_LOGGING)
setup_logger()
