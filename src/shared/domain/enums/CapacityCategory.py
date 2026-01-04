"""
Shared Domain Enum - Capacity Category
"""

from enum import Enum


class CapacityCategory(Enum):
    """
    Enumeration for capacity classification.

    Used to classify capacity values into standard categories.
    """

    NONE = "None"  # Zero capacity
    LOW = "Low"  # Below 33rd percentile
    MEDIUM = "Medium"  # Between 33rd and 66th percentile
    HIGH = "High"  # Above 66th percentile
