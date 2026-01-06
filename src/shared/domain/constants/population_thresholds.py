"""
Population Density Thresholds.
"""


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
