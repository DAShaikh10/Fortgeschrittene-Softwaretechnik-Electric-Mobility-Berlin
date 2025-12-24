"""
Shared Domain Aggregate - Resident Data Aggregate Module.
"""

from dataclasses import dataclass

from src.shared.domain.value_objects import PostalCode


@dataclass
class ResidentDataAggregate:
    """
    Aggregate Root: Represents population data for a postal code area.
    """

    postal_code: PostalCode  # Identity.
    population: int

    def __post_init__(self):
        if self.population < 0:
            raise ValueError("Population cannot be negative")

    def get_population(self) -> int:
        """
        Business logic: Get total population.
        """

        return self.population

    # def get_population_density_category(self) -> str:
    #     """
    #     Business logic: Categorize population density.

    #     Returns:
    #         str: Population density category ("HIGH", "MEDIUM", "LOW").
    #     """

    #     if self.population > 20000:
    #         return "HIGH"
    #     elif self.population > 10000:
    #         return "MEDIUM"
    #     else:
    #         return "LOW"

    # def is_high_density(self) -> bool:
    #     """Business rule"""
    #     return self.population > 15000

    # def calculate_demand_ratio(self, station_count: int) -> float:
    #     """Business calculation"""
    #     return self.population / max(station_count, 1)
