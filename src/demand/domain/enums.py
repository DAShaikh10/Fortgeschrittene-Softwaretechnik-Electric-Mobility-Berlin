"""
Demand Domain Enums.
"""

from enum import Enum


class PriorityLevel(Enum):
    """
    Enumeration for demand priority levels.
    """

    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
