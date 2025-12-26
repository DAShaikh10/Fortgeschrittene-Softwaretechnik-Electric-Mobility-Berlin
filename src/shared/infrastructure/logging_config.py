"""
Centralized Logging Configuration Module.

This module provides a centralized logging configuration for the EVision Berlin application.
"""

import logging
import sys


def setup_logging(level=logging.INFO):
    """
    Configure the root logger with standard formatting.

    Args:
        level: Logging level (default: logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for the given module.

    Args:
        name: The name of the logger (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
