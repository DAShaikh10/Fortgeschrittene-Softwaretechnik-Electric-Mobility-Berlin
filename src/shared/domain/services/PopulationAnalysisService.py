"""
Shared Domain Service - Population Analysis Service Module.
"""


class PopulationAnalysisService:
    """
    Domain Service: Provides business logic for population density and demand analysis.

    This service encapsulates calculations for population density categorization
    and demand ratios, keeping the PopulationData value object pure.
    """

    @staticmethod
    def get_density_category(population: int) -> str:
        """
        Business logic: Categorize population density into standard ranges.

        Categories based on typical urban planning thresholds:
        - HIGH: > 20,000 residents (dense urban area)
        - MEDIUM: 10,000-20,000 residents (suburban/moderate density)
        - LOW: < 10,000 residents (low density/rural)

        Args:
            population (int): The population count.

        Returns:
            str: Population density category.
        """
        if population > 20000:
            return "HIGH"
        if population > 10000:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def is_high_density(population: int) -> bool:
        """
        Business rule: Determine if area is high-density.

        High density threshold set at 15,000+ residents based on
        typical EV infrastructure planning requirements.

        Args:
            population (int): The population count.

        Returns:
            bool: True if population exceeds high-density threshold.
        """
        return population > 15000

    @staticmethod
    def calculate_demand_ratio(population: int, station_count: int) -> float:
        """
        Business calculation: Calculate residents per charging station ratio.

        This provides a simple demand metric for infrastructure planning.

        Args:
            population (int): The population count.
            station_count (int): Number of charging stations in the area.

        Returns:
            float: Residents per station ratio (population if no stations).
        """
        return population / max(station_count, 1)
