"""
Infrastructure Thresholds and Business Constants.
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
