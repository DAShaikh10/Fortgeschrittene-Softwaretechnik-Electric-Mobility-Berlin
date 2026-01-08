"""
Shared Domain Infrastructure Thresholds and Business Constants.
"""


class InfrastructureThresholds:
    """
    Business constants for infrastructure coverage assessment.

    These thresholds are based on urban planning standards and
    EV infrastructure best practices.
    """

    # Station count thresholds for coverage levels
    WELL_EQUIPPED_STATION_COUNT = 5
    WELL_EQUIPPED_FAST_CHARGER_COUNT = 2

    POOR_COVERAGE_THRESHOLD = 5
    ADEQUATE_COVERAGE_THRESHOLD = 5
    GOOD_COVERAGE_STATION_COUNT = 10
    GOOD_COVERAGE_FAST_CHARGER_COUNT = 2
    EXCELLENT_COVERAGE_STATION_COUNT = 20
    EXCELLENT_COVERAGE_FAST_CHARGER_COUNT = 5

    # Demand analysis thresholds
    EXPANSION_NEEDED_RATIO = 3000  # residents per station

    # Coverage assessment thresholds (residents per station)
    CRITICAL_COVERAGE_RATIO = 10000
    POOR_COVERAGE_RATIO = 5000
    ADEQUATE_COVERAGE_RATIO = 2000
    TARGET_COVERAGE_RATIO = 2000.0  # Recommended target

    # Priority level thresholds (residents per station)
    HIGH_PRIORITY_THRESHOLD = 5000
    MEDIUM_PRIORITY_THRESHOLD = 2000

    # Urgency score thresholds
    CRITICAL_URGENCY_THRESHOLD = 10000
    HIGH_URGENCY_THRESHOLD = 5000
    MEDIUM_URGENCY_THRESHOLD = 2000


class PopulationThresholds:
    """
    Business constants for population density classification.

    Based on urban planning standards for density categories:
    - Low density: < 10,000 residents (rural/suburban)
    - Medium density: 10,000-20,000 residents (suburban)
    - High density: > 20,000 residents (urban core)
    """

    # Population density categories
    HIGH_DENSITY_THRESHOLD = 20000
    MEDIUM_DENSITY_THRESHOLD = 10000

    # High density determination for demand analysis
    HIGH_DENSITY_DEMAND_THRESHOLD = 15000


class PostalCodeThresholds:
    """
    Business constants for Berlin postal code validation.

    Berlin postal codes range from 10001 to 14199.
    """

    MIN_BERLIN_POSTAL_CODE = 10000
    MAX_BERLIN_POSTAL_CODE = 14200


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
