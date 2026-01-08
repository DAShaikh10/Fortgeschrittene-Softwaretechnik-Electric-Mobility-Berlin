"""
src.shared.infrastructure - Shared Infrastructure Module.

We allow implicit imports only from the infrastructure layer, for the other layers we enforce explicit imports.
"""

from .logging_config import setup_logging, get_logger

__all__ = [
    "setup_logging",
    "get_logger",
]
