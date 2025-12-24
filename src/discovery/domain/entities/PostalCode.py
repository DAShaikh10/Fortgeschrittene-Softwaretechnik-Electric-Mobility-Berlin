"""
Discovery Domain Entity - Postal Code Module.
"""

from dataclasses import dataclass


@dataclass
class PostalCode:
    """
    Postal Code Entity.
    """

    value: str
