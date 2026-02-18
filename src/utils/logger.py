"""
Central logger configuration for the application.

This module sets up Loguru-based logging, featuring split streams for
standard output and errors, log rotation, and the ability to silence
noisy third-party library logs.
"""

import logging
import sys

from loguru import logger

from src.config.params import DEBUG_LOGS

# List of library names (e.g., 'chromadb', 'httpx') to silence
DEPENDENCIES_WITH_LOGGING: list[str] = []

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def disable_dependency_loggers(dependencies: list[str]) -> None:
    """
    Disables logging for specific third-party dependencies.

    Prevents external library logs from cluttering the application logs
    by setting their 'disabled' flag to True and stopping propagation.

    Parameters
    ----------
    dependencies : list[str]
        A list of library names as strings to be disabled.
    """
    for name in dependencies:
        logging.getLogger(name).disabled = True
        logging.getLogger(name).propagate = False


def setup_logger(debug: bool | None = None) -> None:
    """
    Configures and initializes the Loguru logger handlers.

    Sets up a three-tier logging strategy:
    1. Standard Output: Handles DEBUG/INFO levels (Severity < 30).
    2. Standard Error: Handles WARNING and higher (Severity >= 30).
    3. File: Persistent storage with rotation and compression.

    Parameters
    ----------
    debug : bool, optional
        If True, the base log level is set to 'DEBUG'. If False, it
        defaults to 'INFO'. If None, it uses the logic defined
        within the function.
    """
    # Remove default Loguru handler
    logger.remove()

    # Determine the "Floor" level (DEBUG or INFO)
    base_level = "DEBUG" if debug else "INFO"

    # 1. Console: Standard Output (DEBUG/INFO)
    # Uses a filter to ensure higher severity levels don't duplicate to stdout
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=base_level,
        filter=lambda r: r["level"].no < 30,  # Stop before WARNING
    )

    # 2. Console: Standard Error (WARNING+)
    # This ensures critical issues are highlighted in the error stream
    logger.add(
        sys.stderr,
        format="\n" + LOG_FORMAT,
        level="WARNING",
    )

    # 3. File: Persistent storage (Matches base_level)
    # Configured with rotation (size-based) and retention (time-based)
    logger.add(
        "data/logs/app.log",
        format=LOG_FORMAT,
        level=base_level,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        enqueue=True,  # Thread-safe logging
    )


# --- INITIALIZATION ---
# Run once when module is imported to apply settings globally
disable_dependency_loggers(DEPENDENCIES_WITH_LOGGING)
setup_logger(debug=DEBUG_LOGS)
