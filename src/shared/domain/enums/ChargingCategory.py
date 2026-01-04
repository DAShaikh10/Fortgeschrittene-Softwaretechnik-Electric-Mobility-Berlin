"""
Shared Domain Enum - Charging Category
"""

from enum import Enum


class ChargingCategory(Enum):
    """
    Enumeration for charging station power categories.

    Used to classify charging stations based on their power output.
    """

    NORMAL = "NORMAL"  # < 50 kW (AC charging, home wallboxes)
    FAST = "FAST"  # 50-149 kW (DC fast charging)
    ULTRA = "ULTRA"  # >= 150 kW (Ultra-fast DC charging)
