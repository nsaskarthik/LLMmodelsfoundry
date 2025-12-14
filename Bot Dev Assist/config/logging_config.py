"""Logging configuration and utilities."""

import logging
import os
from typing import Optional

from .app import AppConfig


def setup_logging(app_config: AppConfig) -> logging.Logger:
    """Configure root logger with level/format and optional file output.

    Args:
        app_config: Application configuration

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger()

    # Skip if already configured
    if logger.handlers:
        return logger

    # Set level
    logger.setLevel(app_config.log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler (always)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if configured)
    if app_config.log_path:
        try:
            # Ensure directory exists
            log_dir = os.path.dirname(app_config.log_path)
            os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(app_config.log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.info(f"Logging to file: {app_config.log_path}")
        except Exception as e:
            logger.warning(f"Could not setup file logging: {str(e)}")

    return logger


def with_context(logger: logging.Logger, **context) -> logging.LoggerAdapter:
    """Attach contextual fields (e.g., session_id, user) to log records.

    Args:
        logger: Logger instance
        **context: Context fields to attach

    Returns:
        LoggerAdapter with context
    """
    return logging.LoggerAdapter(logger, extra=context)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        name: Module name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
