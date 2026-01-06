"""
Power and Charging Speed Thresholds.
"""


class PowerThresholds:
    """
    Business constants for charging power categories.

    Based on industry standards for EV charging infrastructure:
    - Normal charging: < 50 kW
    - Fast charging: 50-150 kW
    - Ultra-fast charging: >= 150 kW
    """

    # Power capacity limits
    MAX_REASONABLE_POWER_KW = 1000.0

    # Charging speed categories
    FAST_CHARGING_THRESHOLD_KW = 50.0
    ULTRA_CHARGING_THRESHOLD_KW = 150.0
