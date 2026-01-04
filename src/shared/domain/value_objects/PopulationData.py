"""
Shared Domain Value Object - Population Data Module.
"""

from dataclasses import dataclass

from src.shared.domain.value_objects.PostalCode import PostalCode


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