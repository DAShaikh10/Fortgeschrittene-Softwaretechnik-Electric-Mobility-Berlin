"""
Shared Domain Enum - Population Density Category
"""

from enum import Enum


class PopulationDensityCategory(Enum):
    """
    Enumeration for population density categories.

    Used to classify areas based on population density for infrastructure planning.
    """

    LOW = "LOW"  # < 10,000 residents (low density/rural)
    MEDIUM = "MEDIUM"  # 10,000-20,000 residents (suburban/moderate density)
    HIGH = "HIGH"  # > 20,000 residents (dense urban area)
