"""
Shared Domain Value Object - Population Data Module.
"""

from dataclasses import dataclass

from src.shared.domain.value_objects import PostalCode


@dataclass(frozen=True)
class PopulationData:
    """
    Value Object: Represents immutable population data for a postal code area.

    Business Rules:
    - Population must be non-negative
    - Associated with a valid postal code
    """

    postal_code: PostalCode
    population: int

    def __post_init__(self):
        """Validate population value on creation."""
        if self.population < 0:
            raise ValueError(f"Population cannot be negative, got: {self.population}")

    def get_population(self) -> int:
        """
        Query: Get the population count.

        Returns:
            int: Population count for this postal code area.
        """
        return self.population

    def get_population_density_category(self) -> str:
        """
        Business logic: Categorize population density into standard ranges.

        Categories based on typical urban planning thresholds:
        - HIGH: > 20,000 residents (dense urban area)
        - MEDIUM: 10,000-20,000 residents (suburban/moderate density)
        - LOW: < 10,000 residents (low density/rural)

        Returns:
            str: Population density category.
        """
        if self.population > 20000:
            return "HIGH"
        elif self.population > 10000:
            return "MEDIUM"
        else:
            return "LOW"

    def is_high_density(self) -> bool:
        """
        Business rule: Determine if area is high-density.

        High density threshold set at 15,000+ residents based on
        typical EV infrastructure planning requirements.

        Returns:
            bool: True if population exceeds high-density threshold.
        """
        return self.population > 15000

    def calculate_demand_ratio(self, station_count: int) -> float:
        """
        Business calculation: Calculate residents per charging station ratio.

        This provides a simple demand metric for infrastructure planning.

        Args:
            station_count: Number of charging stations in the area.

        Returns:
            float: Residents per station ratio (population if no stations).
        """
        return self.population / max(station_count, 1)
