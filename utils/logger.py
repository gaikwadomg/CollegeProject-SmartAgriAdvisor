"""
AgriSense AI - Logging Configuration
======================================

Provides a centralized logging setup with rotating file handlers
and colored console output. All modules should use get_logger()
to obtain a properly configured logger instance.

Usage:
    from utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Application started")

Author: AgriSense AI Team
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ── Module-level state ────────────────────────────────────────────────
_initialized = False


def _setup_logging() -> None:
    """
    Initialize the root logger with console and file handlers.
    Called automatically on first get_logger() call.
    """
    global _initialized
    if _initialized:
        return

    # Import here to avoid circular imports at module load time
    from config.settings import Settings

    # Ensure logs directory exists
    Settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger("agrisense")
    root_logger.setLevel(getattr(logging, Settings.LOG_LEVEL, logging.INFO))

    # Prevent duplicate handlers on re-initialization
    if root_logger.handlers:
        _initialized = True
        return

    # ── Log Format ────────────────────────────────────────────────
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_format = logging.Formatter(
        fmt="%(levelname)-8s | %(name)-20s | %(message)s"
    )

    # ── File Handler (Rotating) ───────────────────────────────────
    try:
        file_handler = RotatingFileHandler(
            filename=Settings.LOG_PATH,
            maxBytes=Settings.LOG_MAX_BYTES,
            backupCount=Settings.LOG_BACKUP_COUNT,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
    except (OSError, PermissionError) as e:
        # If file logging fails, continue with console only
        print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    # ── Console Handler ───────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    _initialized = True
    root_logger.info("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance for a module.

    Args:
        name: Module name, typically __name__

    Returns:
        logging.Logger: Configured logger instance under the 'agrisense' hierarchy

    Example:
        logger = get_logger(__name__)
        logger.info("Module loaded successfully")
    """
    _setup_logging()

    # Prefix all loggers under the 'agrisense' namespace
    if not name.startswith("agrisense"):
        logger_name = f"agrisense.{name}"
    else:
        logger_name = name

    return logging.getLogger(logger_name)
