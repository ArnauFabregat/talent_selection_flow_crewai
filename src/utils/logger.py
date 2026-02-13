"""
This file defines the logger object for use within this library's processes.
Other modules from this library should import the `logger` object from here to produce logs.
"""

import logging
import sys
from typing import List

from loguru import logger
from loguru._logger import Logger as LoguruLogger

DEPENDENCIES_WITH_LOGGING = ["prophet", "cmdstanpy"]
LOG_FORMAT = (  # When first defined, this variable was set to the default value of loguru
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
    for dependency in dependencies:
        logging.getLogger(dependency).disabled = True
        logging.getLogger(dependency).propagate = False


def setup_loguru_logger(loguru_logger: LoguruLogger) -> None:
    """
    Sets up loguru's logger with the defined configuration

    Parameters
    ----------
    loguru_logger: LoguruLogger
        The loguru logger as imported from the `loguru` module
    """
    # Remove default logger
    loguru_logger.remove()

    # Set logging levels to corresponding output
    loguru_logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="INFO",
        filter=lambda log_record: log_record["level"].name in ["INFO", "DEBUG"],
    )
    loguru_logger.add(sys.stderr, format=LOG_FORMAT, level="WARNING")


# These functions will be executed here only once, when first imported by another Python module
disable_dependency_loggers(DEPENDENCIES_WITH_LOGGING)
setup_loguru_logger(logger)
